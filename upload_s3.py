#!/usr/bin/env python
# Script for upload to APTrust S3 buckets
# Pasted and adapted from: https://boto3.amazonaws.com/v1/documentation/api/latest/guide/s3-uploading-files.html
# In order to create an UPLOAD PROGRESS BAR, see the webpage above.

import logging
import boto3
from botocore.exceptions import ClientError
from os import listdir, path, makedirs
from shutil import move
from tqdm import tqdm


def upload_file_with_progress(file_name, bucket, obj_name, akey, skey):
    """Upload a file to an S3 bucket with progress bar"""
    if obj_name is None:
        obj_name = path.basename(file_name)
    
    # Create an S3 client
    s3_client = boto3.client('s3', aws_access_key_id=akey, aws_secret_access_key=skey)
    
    # Initialize tqdm with total file size for progress bar
    with tqdm(total=path.getsize(file_name), unit='B', unit_scale=True, desc=obj_name) as pbar:
        # Define callback function to update progress bar
        def progress_callback(bytes_amount):
            pbar.update(bytes_amount)
        
        # Upload the file
        try:
            response = s3_client.upload_file(file_name, bucket, obj_name, Callback=progress_callback)
        except ClientError as e:
            logging.error(e)
            return False
    
    return True


def move_file(source, destination):
    """Move a file from source to destination directory"""
    if not path.exists(destination):
        makedirs(destination)
    move(source, path.join(destination, path.basename(source)))


# Main program
asking = True
while asking:
    demo_prod = input(f'(D)emo or (P)roduction: ').strip()
    if demo_prod.startswith('D') or demo_prod.startswith('d'):
        bucket_name = 'aptrust.receiving.test.uab.edu'
        asking = False
    elif demo_prod.startswith('P') or demo_prod.startswith('p'):
        bucket_name = 'aptrust.receiving.uab.edu'
        asking = False
    else:
        print('\nPlease enter a \'D\' or a \'P\'.\n')

access_key = input(f'Access Key: ').strip()
secret_key = input(f'Secret Key: ').strip()

stop = False
count = 0
uploaded = 0
max_files = 50  # Maximum number of files to upload

while not stop:
    print(f'Please enter the path to the files to upload.')
    upload_dir = input(': ').replace('\"', ' ').replace('\'', ' ').strip()
    if path.isdir(upload_dir):
        stop = True
        print(f'Uploading items in:\n    {upload_dir}')
    else:
        print(f'Incorrect path.\n')
        stop = False

upload_success_dir = input('Enter the directory to move successfully uploaded files: ').strip()

for files in listdir(upload_dir):
    filepath = path.join(upload_dir, files)
    if path.isfile(filepath) and not files.startswith('.') and count < max_files:
        count += 1
        success = upload_file_with_progress(filepath, bucket_name, files, access_key, secret_key)
        if success:
            uploaded += 1
            print(f'Upload of {files} successful.')
            move_file(filepath, upload_success_dir)  # Move successfully uploaded file
        else:
            print(f'Upload of {files} failed.')

print(f'Found {count} files.\nSuccessfully uploaded {uploaded} files.')

