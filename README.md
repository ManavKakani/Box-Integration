# Box Integration Tools

This repository contains Python scripts to sync files from Box to different cloud storage services. These tools provide automated, continuous synchronization between Box and your preferred cloud storage platform.

## Note
- This script starts uploading files from the moment you run it. It will not upload any documents that were previously uploaded to Box before starting the script.

## Available Integrations

- [Box to AWS S3](./box-to-aws/ReadMe.md) - Sync files from Box to an AWS S3 bucket
- [Box to Azure Blob Storage](./box-to-azure/ReadMe.md) - Sync files from Box to Azure Blob Storage with Event Hub notifications

## Features

All integration tools share the following core features:

- **Continuous Monitoring**: Watch for changes in Box folders and sync them automatically
- **One-way Sync**: Transfer files from Box to your cloud storage of choice
- **Smart Updates**: Only sync new or modified files to optimize bandwidth usage
- **Folder Structure Preservation**: Maintain the same directory structure across platforms
- **Detailed Logging**: Track all sync activities and troubleshoot issues easily

## Prerequisites

- Python 3.6 or higher
- Box Developer account with CCG (Client Credentials Grant) enabled
- Account with the respective cloud service provider

## Quick Start

1. Clone this repository:
   ```
   git clone <repository-url>
   cd Box-Integration
   ```

2. Choose your desired integration:
   ```
   cd box-to-aws
   # or
   cd box-to-azure
   ```

3. Follow the specific setup instructions in the integration's README file

## Box Application Setup

All integrations require a Box application with Client Credentials Grant access:

1. Go to the [Box Developer Console](https://developer.box.com/)
2. Create a new server-side OAuth 2.0 application
3. Enable the Client Credentials Grant
4. Generate a client ID and client secret
5. Add necessary scopes including: `read_all_files`, `write_all_files`
6. Get your enterprise ID from the Box Admin Console

## Integration-Specific Documentation

Each integration has its own detailed README with specific setup and usage instructions:

- [Box to AWS S3 Documentation](./box-to-aws/ReadMe.md)
- [Box to Azure Blob Storage Documentation](./box-to-azure/ReadMe.md)

## Use Cases

- **Backup and Archiving**: Automatically backup important Box folders to cloud storage
- **Cloud Migration**: Facilitate transition from Box to another cloud storage provider
- **Multi-cloud Strategy**: Maintain copies of your Box content across different cloud platforms
- **Data Processing Pipelines**: Feed Box data into cloud-based processing systems
