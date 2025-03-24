# Box to AWS Sync

This Python script syncs files from a Box folder to an AWS S3 bucket automatically. The script monitors the specified Box folder for changes and keeps the S3 bucket in sync by:

- This script starts uploading files from the moment you run it. It will not upload any documents that were previously uploaded to Box before starting the script.
- Uploading new files added to Box
- Updating modified files in Box
- Removing files from S3 that were deleted from Box

## Features

- Continuous monitoring with configurable sync interval
- One-way sync from Box to AWS S3
- Detailed logging of all actions
- Handles files and folder structures
- Only syncs files modified after script start

## Prerequisites

- Python 3.6 or higher
- Box Developer account with CCG (Client Credentials Grant) enabled
- AWS account with S3 bucket and appropriate permissions
- AWS credentials with S3 access

## Installation

1. Clone this repository:
   ```
   git clone https://github.com/ManavKakani/Box-Integration.git
   cd Box-Integration/box-to-aws
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

   # AWS S3 Credentials
   AWS_ACCESS_KEY_ID=your_aws_access_key_id
   AWS_SECRET_ACCESS_KEY=your_aws_secret_access_key
   AWS_REGION=your_aws_region
   AWS_S3_BUCKET_NAME=your_s3_bucket_name
   ```

## Box Setup Instructions

1. Go to the [Box Developer Console](https://developer.box.com/)
2. Create a new server-side OAuth 2.0 application
3. Enable the Client Credentials Grant
4. Generate a client ID and client secret
5. Add necessary scopes including: `read_all_files`, `write_all_files`
6. Get your enterprise ID from the Box Admin Console

## Running the Script

1. Ensure your virtual environment is activated:
   ```
   # Windows
   venv\Scripts\activate

   # macOS/Linux
   source venv/bin/activate
   ```

2. Run the script:
   ```
   python box-to-aws.py
   ```

3. The script will start syncing files and output logs to both console and a `sync.log` file.

## Monitoring and Logs

The script produces detailed logs that are saved to `sync.log` in the same directory. These logs include:
- Connection status to Box and AWS
- File operations (uploads, updates, deletions)
- Errors and exceptions

## Stopping the Script

Press `Ctrl+C` to stop the script.

## Troubleshooting

- **Box API Errors**: Verify your Box API credentials and permissions
- **AWS S3 Errors**: Check your AWS credentials and S3 bucket permissions
- **File Not Found Errors**: Ensure the specified Box folder exists within the parent folder

