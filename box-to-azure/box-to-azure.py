import logging
import os
import time
import json
from datetime import datetime
from dotenv import load_dotenv
from boxsdk import CCGAuth, Client
from azure.storage.blob import BlobServiceClient
from azure.eventhub import EventHubProducerClient, EventData
from azure.identity import DefaultAzureCredential

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[logging.StreamHandler(), logging.FileHandler("sync.log")]
)

logger = logging.getLogger()

# Custom logging filter to exclude GET and OPTIONS logs
class NoGetOptionsFilter(logging.Filter):
    def filter(self, record):
        unwanted_messages = ["GET", "OPTIONS", "Response headers", "Response status"]
        return not any(msg in record.getMessage() for msg in unwanted_messages)

for handler in logger.handlers:
    handler.addFilter(NoGetOptionsFilter())

# Box Client Setup
def get_box_client():
    try:
        auth = CCGAuth(
            client_id=os.getenv('BOX_CLIENT_ID'),
            client_secret=os.getenv('BOX_CLIENT_SECRET'),
            enterprise_id=os.getenv('BOX_ENTERPRISE_ID')
        )
        logger.info("Box client setup successful!")
        return Client(auth)
    except Exception as e:
        logger.error(f"Failed to setup Box client: {str(e)}")
        raise

credentials = DefaultAzureCredential()
# Azure Storage Client Setup
def get_azure_client():
    try:
        client = BlobServiceClient(
            account_url=f"https://{os.getenv('AZURE_STORAGE_ACCOUNT_NAME')}.blob.core.windows.net/",
            credential=credentials
        )
        logger.info("Azure Storage Account connection successful.")
        return client
    except Exception as e:
        logger.error(f"Error connecting to Azure Storage Account: {e}")
        raise

# Azure Event Hub Client Setup
def get_eventhub_client():
    try:
        client = EventHubProducerClient(
            fully_qualified_namespace=f"{os.getenv('EVENT_HUB_NAMESPACE')}.servicebus.windows.net",
            eventhub_name=os.getenv('EVENT_HUB_NAME'),
            credential=credentials
        )
        logger.info("Eventhub connection successful.")
        return client
    except Exception as e:
        logger.error(f"Error connecting to Azure Storage Account: {e}")
        raise

# Get Box Folder ID
def get_folder_id_by_name(client, folder_name):
    for item in client.folder(folder_id=os.getenv('BOX_PARENT_FOLDER_ID')).get_items():
        if item.type == 'folder' and item.name == folder_name:
            return item.id
    raise Exception(f"Folder '{folder_name}' not found")

# Parse Timestamp
def parse_timestamp(time_value):
    if isinstance(time_value, str):
        return datetime.fromisoformat(time_value.replace('Z', '+00:00')).timestamp()
    return time_value.timestamp()

# Upload to Azure
def upload_to_azure(blob_service_client, file_path, file_content):
    try:
        blob_client = blob_service_client.get_blob_client(
            container=os.getenv('AZURE_CONTAINER_NAME'), blob=file_path
        )
        blob_client.upload_blob(file_content, overwrite=True)
        logger.info(f"Uploaded: {file_path}")

        # Send structured event
        send_event_to_eventhub(file_path, "upload")
    except Exception as e:
        logger.error(f"Failed to upload {file_path}: {e}")

# Delete from Azure
def delete_from_azure(blob_service_client, file_path):
    try:
        blob_client = blob_service_client.get_blob_client(
            container=os.getenv('AZURE_CONTAINER_NAME'), blob=file_path
        )
        blob_client.delete_blob()
        logger.info(f"Deleted: {file_path}")

        # Send structured event
        send_event_to_eventhub(file_path, "delete")
    except Exception as e:
        logger.error(f"Failed to delete {file_path}: {e}")

# Send event to Azure Event Hub
def send_event_to_eventhub(file_path, event_type):
    try:
        producer = get_eventhub_client()
        event_data_batch = producer.create_batch()

        # Construct dynamic payload
        payload = {
            "file_name": os.path.basename(file_path),
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "file_path": file_path,
            "event_type": event_type
        }

        event_data_batch.add(EventData(json.dumps(payload)))  # Serialize to JSON
        producer.send_batch(event_data_batch)
        logger.info(f"Event sent to Event Hub: {payload}")
    except Exception as e:
        logger.error(f"Failed to send event to Event Hub: {e}")

# Get list of files in Azure Storage
def list_azure_files(blob_service_client):
    container_client = blob_service_client.get_container_client(os.getenv('AZURE_CONTAINER_NAME'))
    return {blob.name for blob in container_client.list_blobs()}

# Track Uploaded Files (To Avoid Duplicate Uploads)
uploaded_files = {}

# Store the script start time to avoid past files
start_time = time.time()

# Process Box Folder (Upload Only When Modified After Start Time)
def process_box_folder(client, box_folder_id, blob_service_client, parent_path=""):
    global uploaded_files, start_time
    items = client.folder(folder_id=box_folder_id).get_items()
    box_files = set()  # Track files present in Box

    for item in items:
        if item.type == 'file':
            file_info = client.file(item.id).get()
            modified_timestamp = parse_timestamp(file_info.modified_at)
            file_path = f"{parent_path}{item.name}"
            box_files.add(file_path)

            # Upload only if modified after script start
            if modified_timestamp >= start_time:
                if file_path not in uploaded_files or modified_timestamp > uploaded_files[file_path]:
                    logger.info(f"Uploading {file_path} (Modified: {datetime.fromtimestamp(modified_timestamp)})")
                    file_content = client.file(item.id).content()
                    upload_to_azure(blob_service_client, file_path, file_content)
                    uploaded_files[file_path] = modified_timestamp  # Update last uploaded timestamp
                    print("--------------------------------------------")
                    logger.info("Checking for new or updated files...")

        elif item.type == 'folder':
            box_files.update(process_box_folder(client, item.id, blob_service_client, f"{parent_path}{item.name}/"))

    return box_files  # Return all files found in Box

# Sync and Cleanup Azure
def sync():
    box_client = get_box_client()
    blob_service_client = get_azure_client()
    box_folder_id = get_folder_id_by_name(box_client, os.getenv('BOX_FOLDER_NAME'))
    
    sync_interval = int(os.getenv('SYNC_INTERVAL', 5))  # Sync interval (seconds)
    logger.info("Checking for new or updated files...")
    while True:
        
        box_files = process_box_folder(box_client, box_folder_id, blob_service_client)
        azure_files = list_azure_files(blob_service_client)

        # Delete files in Azure that are no longer in Box
        for azure_file in azure_files:
            if azure_file not in box_files:
                logger.info(f"Deleting {azure_file} from Azure (File no longer exists in Box)")
                delete_from_azure(blob_service_client, azure_file)
                print("--------------------------------------------")
                logger.info("Checking for new or updated files...")

        time.sleep(sync_interval)


if __name__ == "__main__":
    sync()
