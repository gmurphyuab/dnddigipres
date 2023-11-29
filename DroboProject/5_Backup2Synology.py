import os, shutil, hashlib, csv, time
from time import strftime


def calculate_checksum(file_path, hash_algorithm="md5", chunk_size=4096):
    hasher = hashlib.new(hash_algorithm)
    with open(file_path, "rb") as f:
        while chunk := f.read(chunk_size):
            hasher.update(chunk)
    return hasher.hexdigest()

def check_then_copy(synology, drobo, hash_algorithm="md5"):
    destination = os.listdir(synology)
    source = os.listdir(drobo)
    
    if len(source) == 0:
        print('Error: Drobo outbox folder is empty.')
        return
    
    if len(destination) > 0:
        print('Error: Destination folder is NOT empty.')
        return
    

    num_files_copied = 0
    copied_files_md5s = []  # To store checksums of copied files
        
    for fname in source:
        
        source_path = os.path.join(drobo, fname)
        destination_path = os.path.join(synology, fname)

        # Calculate source file checksum before copying
        source_md5s = calculate_checksum(source_path, hash_algorithm)
            
        shutil.copy2(source_path, destination_path)
        num_files_copied += 1
            
        # Calculate destination file checksum after copying
        destination_md5s = calculate_checksum(destination_path, hash_algorithm)
            
        copied_files_md5s.append((fname, source_md5s, destination_md5s))
        
    print(f'{num_files_copied} files copied from {drobo} to {synology}')
        
    csv_directory = 'Q:/Processing/transfer_manifests'
        
    # Generate the CSV filename based on the current date
    csv_filename = os.path.join(csv_directory, f'drobotransfer_{time.strftime("%Y%b%d_%H%M%S")}.csv')

        
    # Write checksums to a CSV file
    with open(csv_filename, mode="w", newline="") as csvfile:
        csv_writer = csv.writer(csvfile)
        csv_writer.writerow(["Filename", "Source Checksum", "Destination Checksum"])
        csv_writer.writerows(copied_files_md5s)
        
    print(f"Checksums written to {csv_filename}")

drobo = input('Enter Drobo folder path: ')
synology = input('Enter Synology destination folder: ')
hash_algorithm = "md5" 

check_then_copy(synology, drobo, hash_algorithm)
