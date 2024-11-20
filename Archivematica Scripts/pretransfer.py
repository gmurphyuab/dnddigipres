'''
Script to move preservation tars from Synology to Archivematica production machine
and prepare them for transfer. 

To learn more about this script, visit: https://uab-libraries.atlassian.net/wiki/x/AQAEIw

'''
import os
import shutil
import tarfile
from pathlib import Path

def copy_and_process_tar_files(src_dir, dest_dir, xml_file):
    """
    Copies tar files from src_dir to dest_dir, untars them, moves contents up a level,
    and places the processing configuration XML file in the first level of each untarred directory.
    Deletes the tar files from dest_dir after processing.

    :param src_dir: Source directory containing tar files. This is on the Synology NAS. 
    :param dest_dir: Destination directory for tar files and untarred contents. This is the staging folder in /home/amadmin.
    :param xml_file: Path to the Processing Configuration XML file to copy into untarred directories. 
    
    """
    src_dir = Path(src_dir)
    dest_dir = Path(dest_dir)
    xml_file = Path(xml_file)

    # Ensure destination directory exists
    dest_dir.mkdir(parents=True, exist_ok=True)
    
    # Iterate over all tar files in the source directory
    for tar_path in src_dir.glob('*.tar'):
        try:
            # Copy tar file to destination
            dest_tar_path = dest_dir / tar_path.name
            shutil.copy(tar_path, dest_tar_path)
            
            # Create a directory for the extracted contents
            extract_dir = dest_dir / tar_path.stem
            extract_dir.mkdir(exist_ok=True)
            
            # Untar the file into its extraction directory
            with tarfile.open(dest_tar_path) as tar:
                tar.extractall(path=extract_dir)
            
            # Move contents up one level
            for item in extract_dir.iterdir():
                if item.is_dir():
                    for subitem in item.iterdir():
                        subitem.rename(extract_dir / subitem.name)
                    item.rmdir()
            
            # Copy the XML file to the first level of the untarred directory
            if xml_file.exists():
                shutil.copy(xml_file, extract_dir / xml_file.name)
            else:
                print(f"Warning: XML file not found at {xml_file}")
            
            # Print success message for each processed tar file
            print(f"Successfully processed {tar_path.name}")
        
        except Exception as e:
            # Log error message and continue with the next tar file
            print(f"Error processing {tar_path.name}: {e}")
    
    # Delete all tar files in the destination directory
    for tar_file in dest_dir.glob('*.tar'):
        tar_file.unlink()
    print("All tar files have been deleted from the destination directory.")

if __name__ == "__main__":
    source_directory = "/path/to/source"
    destination_directory = "/path/to/destination"
    xml_file_path = "path/to/processing config XML file"

    copy_and_process_tar_files(source_directory, destination_directory, xml_file_path)
