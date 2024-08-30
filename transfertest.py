import os
import requests
import shutil
from pathlib import Path
import base64
import logging

# Configure logging
logging.basicConfig(
    filename='/home/2archivematica/transfer_source/transfer_log.log',  # Update with your desired log file path
    level=logging.INFO,
    format='%(asctime)s %(levelname)s:%(message)s'
)

logging.info("\n")
# Environment variables for security
#API_KEY = os.getenv('ARCHIVEMATICA_API_KEY')
#USER_NAME = os.getenv('ARCHIVEMATICA_USER_NAME')
API_KEY = '73e0503d6340e2d293aa8def2837eb0750e5ae6d'
USER_NAME = 'dndadmin'
TRANSFER_URL = 'http://192.168.75.116/api/transfer/start_transfer/'
SOURCE_DIR = '/home/2archivematica/transfer_source/Processing/ready_to_package'          
PROCESSED_DIR = '/home/2archivematica/transfer_source/Processing/transferred'    
ACCESSION_NUMBER = '0001'               
PROCESSING_TYPE = 'zipped bag'                 

def encode_path(file_path):
    """
    Encodes the file path in base64 as required by the API.
    """
    # Ensure the path is absolute and correctly formatted
    absolute_path = os.path.abspath(file_path)
    encoded = base64.b64encode(absolute_path.encode('utf-8')).decode('utf-8')
    return encoded

def transfer_bag(file_path):
    """
    Transfers a single zipped bag to Archivematica.
    """
    try:
        # Prepare headers
        headers = {
            'Authorization': f'ApiKey {USER_NAME}:{API_KEY}',
            'Content-Type': 'application/x-www-form-urlencoded'
        }

        # Encode the file path
        encoded_path = encode_path(file_path)

        # Prepare data payload
        data = {
            'name': Path(file_path).stem,               # Transfer name derived from file name
            'type': PROCESSING_TYPE,                    # Processing configuration type
            'accession': ACCESSION_NUMBER,              # Accession number
            'paths[]': encoded_path,                    # Encoded path to the zipped bag
            'rows_id[]': ''                             # Include if required; else, can be omitted
        }

        # Make the POST request to initiate the transfer
        response = requests.post(TRANSFER_URL, headers=headers, data=data)

        # Check the response status
        if response.status_code == 200:
            logging.info(f"Successfully transferred {file_path}")
            return True
        else:
            logging.error(f"Failed to transfer {file_path}: {response.status_code} {response.text}")
            return False

    except Exception as e:
        logging.error(f"Exception occurred while transferring {file_path}: {str(e)}")
        return False

def process_directory():
    """
    Processes all zipped bags in the source directory.
    """
    try:
        # Ensure the processed directory exists
        os.makedirs(PROCESSED_DIR, exist_ok=True)

        # Iterate over all files in the source directory
        for file_name in os.listdir(SOURCE_DIR):
            if file_name.endswith('.tar.gz'):
                file_path = os.path.join(SOURCE_DIR, file_name)
                
                # Transfer the bag
                if transfer_bag(file_path):
                    # Move the file to the processed directory after successful transfer
                    shutil.move(file_path, os.path.join(PROCESSED_DIR, file_name))
                    logging.info(f"Moved {file_path} to {PROCESSED_DIR}")
                else:
                    logging.warning(f"Transfer failed for {file_path}; file remains in source directory.")

    except Exception as e:
        logging.error(f"Exception occurred while processing directory: {str(e)}")

if __name__ == "__main__":
    process_directory()
