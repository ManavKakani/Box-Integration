# Box to Azure Sync

This Python script syncs files from a Box folder to Azure Blob Storage automatically. The script monitors the specified Box folder for changes and keeps the Azure Blob Storage container in sync by:

- Uploading new files added to Box
- Updating modified files in Box
- Removing files from Azure that were deleted from Box
- Sending events to Azure Event Hub for each file operation

## Features

- Continuous monitoring with configurable sync interval
- One-way sync from Box to Azure Blob Storage
- Event notifications via Azure Event Hub
- Detailed logging of all actions
- Handles files and folder structures
- Only syncs files modified after script start

## Prerequisites

- Python 3.6 or higher
- Box Developer account with CCG (Client Credentials Grant) enabled
- Azure account with the following resources:
  - Azure Blob Storage account and container
  - Azure Event Hub namespace and Event Hub
- Azure credentials with appropriate permissions

## Installation

1. Clone this repository:
   ```
   git clone https://github.com/ManavKakani/Box-Integration.git
   cd Box-Integration/box-to-azure
   ```

2. Create and activate a virtual environment:
   ```
   # On Windows
   python -m venv venv
   venv\Scripts\activate

   # On macOS/Linux
   python3 -m venv venv
   source venv/bin/activate
   ```

3. Install dependencies:
   ```
   pip install -r requirements.txt
   ```

4. Configure the environment variables in .env file:

   Edit the `.env` file with your credentials:

   ```
   # Box API Credentials
   BOX_CLIENT_ID=your_box_client_id
   BOX_CLIENT_SECRET=your_box_client_secret
   BOX_ENTERPRISE_ID=your_box_enterprise_id
   BOX_PARENT_FOLDER_ID=your_box_parent_folder_id  # ID of the parent folder
   BOX_FOLDER_NAME=your_box_folder_name  # Name of the folder to sync

   # Azure Storage Account
   AZURE_STORAGE_ACCOUNT_NAME=your_storage_account_name
   AZURE_CONTAINER_NAME=your_container_name  # Name of the Azure Blob Storage container

   # Azure Event Hub
   EVENT_HUB_NAMESPACE=your_event_hub_namespace  # Event Hub namespace
   EVENT_HUB_NAME=your_event_hub_name  # Name of the Event Hub
   ```

## Box Setup Instructions

1. Go to the [Box Developer Console](https://developer.box.com/)
2. Create a new server-side OAuth 2.0 application
3. Enable the Client Credentials Grant
4. Generate a client ID and client secret
5. Add necessary scopes including: `read_all_files`, `write_all_files`
6. Get your enterprise ID from the Box Admin Console

## Azure Setup Instructions

1. **Azure Blob Storage**:
   - Create an Azure Storage Account in the Azure Portal
   - Create a container within the Storage Account
   - Note the Storage Account name and container name

2. **Azure Event Hub**:
   - Create an Event Hub Namespace in the Azure Portal
   - Create an Event Hub within the namespace
   - Note the Event Hub Namespace and Event Hub name

3. **Azure Credentials**:
   - The script uses DefaultAzureCredential, which supports multiple authentication methods
   - For development, you can authenticate using:
     - Azure CLI (`az login`)
     - Visual Studio Code Azure extension
     - Environment variables (AZURE_CLIENT_ID, AZURE_CLIENT_SECRET, AZURE_TENANT_ID)

## Running the Script

1. Ensure your virtual environment is activated:
   ```
   # Windows
   venv\Scripts\activate

   # macOS/Linux
   source venv/bin/activate
   ```

2. Make sure you're authenticated with Azure (if using Azure CLI):
   ```
   az login
   ```

3. Run the script:
   ```
   python box-to-azure.py
   ```

4. The script will start syncing files and output logs to both console and a `sync.log` file.

## Monitoring and Logs

The script produces detailed logs that are saved to `sync.log` in the same directory. These logs include:
- Connection status to Box and Azure services
- File operations (uploads, updates, deletions)
- Event Hub message details
- Errors and exceptions

## Event Hub Integration

For each file operation, the script sends a structured event to the specified Azure Event Hub. The event includes:
- File name
- File path
- Event type (upload or delete)
- Timestamp

These events can be consumed by other Azure services like:
- Azure Functions
- Azure Stream Analytics
- Azure Logic Apps
- Custom applications

## Stopping the Script

Press `Ctrl+C` to stop the script.

## Troubleshooting

- **Box API Errors**: Verify your Box API credentials and permissions
- **Azure Authentication Errors**: Check your Azure authentication method and credentials
- **Azure Blob Storage Errors**: Verify your Storage Account name and container exist
- **Azure Event Hub Errors**: Ensure your Event Hub namespace and Event Hub exist
- **File Not Found Errors**: Ensure the specified Box folder exists within the parent folder
