import logging
import os
import time
import json
from datetime import datetime
from dotenv import load_dotenv
from boxsdk import CCGAuth, Client
import boto3

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

# AWS S3 Client Setup
def get_s3_client():
    try:
        client = boto3.client(
            's3',
            aws_access_key_id=os.getenv('AWS_ACCESS_KEY_ID'),
            aws_secret_access_key=os.getenv('AWS_SECRET_ACCESS_KEY'),
            region_name=os.getenv('AWS_REGION')
        )
        logger.info("AWS S3 connection successful.")
        return client
    except Exception as e:
        logger.error(f"Error connecting to AWS S3: {e}")
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

# Upload to AWS S3
def upload_to_s3(s3_client, file_path, file_content):
    try:
        bucket_name = os.getenv('AWS_S3_BUCKET_NAME')
        s3_client.put_object(Bucket=bucket_name, Key=file_path, Body=file_content)
        logger.info(f"Uploaded to S3: {file_path}")
    except Exception as e:
        logger.error(f"Failed to upload {file_path} to S3: {e}")

# Delete from AWS S3
def delete_from_s3(s3_client, file_path):
    try:
        bucket_name = os.getenv('AWS_S3_BUCKET_NAME')
        s3_client.delete_object(Bucket=bucket_name, Key=file_path)
        logger.info(f"Deleted from S3: {file_path}")
    except Exception as e:
        logger.error(f"Failed to delete {file_path} from S3: {e}")

# Get list of files in S3
def list_s3_files(s3_client):
    bucket_name = os.getenv('AWS_S3_BUCKET_NAME')
    objects = s3_client.list_objects_v2(Bucket=bucket_name)
    return {obj['Key'] for obj in objects.get('Contents', [])}

# Track Uploaded Files (To Avoid Duplicate Uploads)
uploaded_files = {}

# Store the script start time to avoid past files
start_time = time.time()

# Process Box Folder (Upload Only When Modified After Start Time)
def process_box_folder(client, box_folder_id, s3_client, parent_path=""):
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
                    upload_to_s3(s3_client, file_path, file_content)
                    uploaded_files[file_path] = modified_timestamp  # Update last uploaded timestamp
                    logger.info("Checking for new or updated files...")

        elif item.type == 'folder':
            box_files.update(process_box_folder(client, item.id, s3_client, f"{parent_path}{item.name}/"))

    return box_files  # Return all files found in Box

# Sync and Cleanup S3
def sync():
    box_client = get_box_client()
    s3_client = get_s3_client()
    box_folder_id = get_folder_id_by_name(box_client, os.getenv('BOX_FOLDER_NAME'))
    
    sync_interval = int(os.getenv('SYNC_INTERVAL', 5))  # Sync interval (seconds)
    logger.info("Checking for new or updated files...")
    while True:
        
        box_files = process_box_folder(box_client, box_folder_id, s3_client)
        s3_files = list_s3_files(s3_client)

        # Delete files in S3 that are no longer in Box
        for s3_file in s3_files:
            if s3_file not in box_files:
                logger.info(f"Deleting {s3_file} from S3 (File no longer exists in Box)")
                delete_from_s3(s3_client, s3_file)
                logger.info("Checking for new or updated files...")

        time.sleep(sync_interval)


if __name__ == "__main__":
    sync()
