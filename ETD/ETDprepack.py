import os
import csv
import xml.etree.ElementTree as ET
from datetime import datetime
import subprocess
from lxml import etree
import shutil
import pandas as pd

# Function to extract information from the XML file
def extract_info(xml_file_path):
    try:
        tree = ET.parse(xml_file_path)
        root = tree.getroot()

        # Extracting information from the XML elements
        surname = root.find('.//DISS_surname').text
        title = root.find('.//DISS_title').text
        comp_date = root.find('.//DISS_comp_date').text

        return [surname, title, comp_date]
    except Exception as e:
        print(f"Error processing {xml_file_path}: {str(e)}")
        return [None, None, None]

# Function to extract ProQuestID from XML filename (ProQuestID is NOT an XML element in ProQuest's XML file)
def extract_proquest_id(xml_filename):
    try:
        # Split the filename by underscores and get the second to last part
        parts = xml_filename.split('_')
        proquest_id = parts[-2]
        return proquest_id
    except Exception as e:
        print(f"Error extracting ProQuestID from {xml_filename}: {str(e)}")
        return None

# Function to remove PII elements from the XML file
def remove_elements_from_xml(xml_file_path):
    try:
        parser = etree.XMLParser(remove_blank_text=True)
        tree = etree.parse(xml_file_path, parser)
        root = tree.getroot()

        # Define the elements to remove
        elements_to_remove = [
            ('DISS_contact', None),
            ('DISS_contact', None),
            ('DISS_citizenship', None),
        ]

        # Iterate through the elements to remove
        for element_tag, element_value in elements_to_remove:
            xpath_expr = f'//{element_tag}'
            if element_value is not None:
                xpath_expr += f'[text()="{element_value}"]'

            elements = root.xpath(xpath_expr)
            for element in elements:
                element.getparent().remove(element)

        # Save the modified XML back to the file with pretty-printing
        tree.write(xml_file_path, encoding='utf-8', xml_declaration=True, pretty_print=True)

        print(f'Removed elements from {xml_file_path}')
    except Exception as e:
        print(f'Error processing {xml_file_path}: {e}')

# Function to walk the directory and collect first-level subdirectory names
def collect_first_level_subdirectories(directory):
    subdirectories = []
    for entry in os.listdir(directory):
        if os.path.isdir(os.path.join(directory, entry)):
            subdirectories.append(os.path.join(directory, entry))
    return subdirectories

def move_subfolders_up(target_directory):

    # Iterate through top-level folders in the target directory
    for root, dirs, files in os.walk(target_directory):
        for dir_name in dirs:
            top_lvl_folder = os.path.join(root, dir_name)

            # Check if the top-level folder contains a subdirectory
            sub_folders = [os.path.join(top_lvl_folder, subfolder) for subfolder in os.listdir(top_lvl_folder) if os.path.isdir(os.path.join(top_lvl_folder, subfolder))]

            if sub_folders:
                # Move files from lowest subdirectory to top level folder
                for sub_folder in sub_folders:
                    for item in os.listdir(sub_folder):
                        source = os.path.join(sub_folder, item)

                        # Append "_supp" to the file name (but before the file extension)
                        base_name, file_extension = os.path.splitext(item)
                        new_item_name = f"{base_name}_supp{file_extension}"

                        destination = os.path.join(top_lvl_folder, new_item_name)
                        shutil.move(source, destination)

                    # Delete the empty lowest subdirectory 
                    shutil.rmtree(sub_folder)

# Function to rename subdirectories using the provided naming convention and user input
def rename_subdirectories(subdirectories, folders_csv, start_number):
    with open(folders_csv, 'w', newline='') as csv_file1:
        csv_writer = csv.writer(csv_file1)
        csv_writer.writerow(['Original Folder', 'UUID'])

        for index, subdir in enumerate(subdirectories):
            new_number = start_number + index
            new_name = f'GRAD_ETD{new_number:06d}'  # Generating the new name
            os.rename(subdir, os.path.join(os.path.dirname(subdir), new_name))
            csv_writer.writerow([os.path.basename(subdir), new_name])

def rename_files_in_folders(root_directory):
    for folder_name, _, files in os.walk(root_directory):
        folder_base = os.path.basename(folder_name)
        suppfile_counter = 3
        file_counter=1

        for file_name in files:
            file_base, file_extension = os.path.splitext(file_name)

            # Check if the file name already contains "_supp"
            if "_supp" in file_base:
                new_file_name = f"{folder_base}_{'{:04d}a'.format(suppfile_counter)}{file_extension}"
                suppfile_counter += 1
            else:
                new_file_name = f"{folder_base}_{'{:04d}a'.format(file_counter)}{file_extension}"
                file_counter += 1

            old_path = os.path.join(folder_name, file_name)
            new_path = os.path.join(folder_name, new_file_name)

            os.rename(old_path, new_path)

def merge_and_delete_csv_files(folders_csv, xml_csv, merged_csv):
    try:
        # Read the CSV files into DataFrames
        df1 = pd.read_csv(folders_csv)
        df2 = pd.read_csv(xml_csv)

        # Merge the DataFrames (you can specify how to merge, e.g., 'inner', 'outer', 'left', 'right')
        merged_df = pd.concat([df1, df2], axis=1)

        # Write the merged DataFrame to a new CSV file
        merged_df.to_csv(merged_csv, index=False)

        # Delete the old CSV files
        os.remove(folders_csv)
        os.remove(xml_csv)

        print(f'Merged data saved to {merged_csv}')
        print(f'{folders_csv} and {xml_csv} deleted.')
    except Exception as e:
        print(f"An error occurred: {str(e)}")


if __name__ == "__main__":

    # Directory to walk through
    root_directory = input('Enter directory path: ')

    # Get the starting UUID number
    start_number = int(input("Enter the starting UUID number: "))

    # Get the current date and year
    current_datetime = datetime.now().strftime('%Y-%m-%d_%H-%M-%S')

    # Create a CSV file name with the current day and year
    folders_csv = f'folders_csv_{current_datetime}.csv'
    xml_csv = f'xml_csv_{current_datetime}.csv'
    merged_csv = f'ETD_batch_metadata_{current_datetime}.csv'

    # Move files up from second-level subdirectories and delete empty second-level subdirectories
    move_subfolders_up(root_directory)

    # Collect first-level subdirectory names after processing second-level subdirectories
    first_level_subdirectories = collect_first_level_subdirectories(root_directory)

    # Rename subdirectories with the provided naming convention and user input
    rename_subdirectories(first_level_subdirectories, folders_csv, start_number)
    
    # Open the CSV file for writing
    with open(xml_csv, 'a', newline='', encoding='utf-8') as csv_file2:
        csv_writer = csv.writer(csv_file2)

        # Write the header row
        csv_writer.writerow(['Last Name', 'Title', 'Year', 'ProQuestID'])

        # Walk through the directory
        for dirpath, _, filenames in os.walk(root_directory):
            for filename in filenames:
                if filename.endswith('.xml'):  # Check if the file is an XML file
                    xml_file_path = os.path.join(dirpath, filename)
                    info = extract_info(xml_file_path)
                    folder_name = os.path.basename(dirpath)  # Get the folder name only

                    # Extract ProQuestID from XML filename
                    proquest_id = extract_proquest_id(filename)

                    # Remove elements from the XML file
                    remove_elements_from_xml(xml_file_path)

                    csv_writer.writerow([*info, proquest_id])

    #Merge two csv's into new file and delete initial csv's
    merge_and_delete_csv_files(folders_csv, xml_csv, merged_csv)

    #rename files to UUID convention
    rename_files_in_folders(root_directory)

    subprocess.Popen(['start', 'excel', merged_csv], shell=True)
