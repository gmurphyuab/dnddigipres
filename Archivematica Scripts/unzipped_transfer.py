import os
import requests
import logging
import base64
import time
import datetime
import shutil
import socket
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Logging configuration
logging.basicConfig(
    filename='',
    level=logging.INFO,
    format='%(asctime)s %(levelname)s:%(message)s'
)

logging.info("\n")

# Detect local IP address
def get_local_ip():
    try:
        hostname = socket.gethostname()
        local_ip = socket.gethostbyname(hostname)
        logging.info(f"Detected local IP address: {local_ip}")
        return local_ip
    except Exception as e:
        logging.error(f"Error retrieving local IP address: {e}")
        return None

# Use detected IP to construct URLs
local_ip = get_local_ip()
if not local_ip:
    raise SystemExit("Failed to retrieve the local IP address.")

TRANSFER_URL = f'http://{local_ip}/api/transfer/start_transfer/'
APPROVAL_URL = f'http://{local_ip}/api/transfer/approve'

location_uuid = os.getenv('LOCATION_UUID')
API_KEY = os.getenv('API_KEY')
USER_NAME = os.getenv('USER_NAME')

SOURCE_DIR = '/path/to/transfer_source'
PROCESSED_DIR = '/path/to/processed/directory'
PROCESSING_TYPE = 'unzipped bag'

# Approval headers
approval_headers = {
    'Authorization': f'ApiKey {USER_NAME}:{API_KEY}',
    'Content-Type': 'application/x-www-form-urlencoded',
    'Host': 'redacted'
}

def start_transfer(folder_name, folder_path):
    path_to_encode = f'{location_uuid}:{folder_path}'
    encoded_path = base64.b64encode(path_to_encode.encode('utf-8')).decode('utf-8')

    data = {
        'name': folder_name,
        'type': PROCESSING_TYPE,
        'accession': folder_name,
        'paths[]': encoded_path
    }

    headers = {
        'Authorization': f'ApiKey {USER_NAME}:{API_KEY}',
        'Content-Type': 'application/x-www-form-urlencoded'
    }

    try:
        response = requests.post(TRANSFER_URL, headers=headers, data=data)
        logging.info(f"API response for {folder_name}: {response.json()}")

        if response.status_code == 200:
            logging.info(f"Successfully initiated transfer: {folder_name}")
            return True
        else:
            logging.error(f"Failed to initiate transfer {folder_name}: {response.status_code} {response.json()}")
            return False
    except Exception as e:
        logging.error(f"Exception occurred while transferring {folder_name}: {str(e)}")
        return False

def approve_transfer():
    """Approves all transfers in the approval directory."""
    approval_dir = '/var/archivematica/sharedDirectory/watchedDirectories/activeTransfers/baggitDirectory'

    for approval_folder in os.listdir(approval_dir):
        approval_data = {
            'directory': approval_folder,
            'type': PROCESSING_TYPE,
            'rows_id[]': ''
        }

        try:
            approval_response = requests.post(APPROVAL_URL, headers=approval_headers, data=approval_data)
            approval_response.raise_for_status()

            logging.info(f"Successfully approved transfer for directory: {approval_folder}")
        except requests.exceptions.RequestException as e:
            logging.error(f"Error approving transfer for directory: {approval_folder}, Error: {e}")

def move_processed_directory(folder_path):
    """Moves the processed directory to the PROCESSED_DIR."""
    try:
        shutil.move(folder_path, PROCESSED_DIR)
        logging.info(f"Moved {folder_path} to {PROCESSED_DIR}")
    except Exception as e:
        logging.error(f"Failed to move {folder_path} to {PROCESSED_DIR}: {e}")

# Step 1: Initiate transfers for all directories in SOURCE_DIR (sorted alphanumerically)
for folder_name in sorted(os.listdir(SOURCE_DIR)):
    folder_path = os.path.join(SOURCE_DIR, folder_name)

    if os.path.isdir(folder_path):
        start_transfer(folder_name, folder_path)

# Pause script to account for potential delay in Step 1 finishing.
time.sleep(10)

# Step 2: Approve Transfers
approve_transfer()

# Step 3: Move processed directories to PROCESSED_DIR
for folder_name in sorted(os.listdir(SOURCE_DIR)):
    folder_path = os.path.join(SOURCE_DIR, folder_name)

    if os.path.isdir(folder_path):
        move_processed_directory(folder_path)
