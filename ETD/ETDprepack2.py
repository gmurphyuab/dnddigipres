import os, csv, subprocess, shutil, zipfile
import pandas as pd
from datetime import datetime
from lxml import etree
from PyPDF2 import PdfFileReader


def unzip(root_directory): 
    directory = os.path.abspath(root_directory)
    for filename in os.listdir(directory):
        file_path = os.path.join(directory, filename)

        if zipfile.is_zipfile(file_path):
            extract_path = os.path.join(directory, os.path.splitext(filename)[0])
            os.makedirs(extract_path, exist_ok=True)

            with zipfile.ZipFile(file_path, 'r') as zip_ref:
                zip_ref.extractall(extract_path)

            os.remove(file_path)

def extract_info(xml_file_path):
    try:
        tree = etree.parse(xml_file_path)
        root = tree.getroot()
        surname = root.findtext('.//DISS_surname')
        title = root.findtext('.//DISS_title')
        comp_date = root.findtext('.//DISS_comp_date')

        return [surname, title, comp_date]
    except Exception as e:
        print(f"Error processing {xml_file_path}: {str(e)}")
        return [None, None, None]

# Function to remove PII elements from the XML file
def remove_elements_from_xml(xml_file_path):
    try:
        parser = etree.XMLParser(remove_blank_text=True)
        tree = etree.parse(xml_file_path, parser)
        root = tree.getroot()

        # Define the elements to remove
        elements_to_remove = [
            ('DISS_contact', None),
            ('DISS_citizenship', None),
        ]

        for element_tag, _ in elements_to_remove:
            xpath_expr = f'//{element_tag}'
            elements = root.xpath(xpath_expr)
            for element in elements:
                element.getparent().remove(element)

        tree.write(xml_file_path, encoding='utf-8', xml_declaration=True, pretty_print=True)

        print(f'Removed elements from {xml_file_path}')
    except Exception as e:
        print(f'Error processing {xml_file_path}: {e}')

def get_pdf_filename(folder_path):
    pdf_files = [f for f in os.listdir(folder_path) if f.endswith('.pdf')]
    
    if not pdf_files:
        return None
    elif len(pdf_files) == 1:
        return os.path.splitext(pdf_files[0])[0]  
    else:
        print("\n Multiple PDF files found in the folder:")
        for i, pdf_file in enumerate(pdf_files, start=1):
            print(f"{i}. {pdf_file}")

        selection = input("Enter the number corresponding to the PDF file to use: ")
        try:
            selection_index = int(selection) - 1
            return os.path.splitext(pdf_files[selection_index])[0]
        except (ValueError, IndexError):
            print("Invalid selection. Using the first PDF file.")
            return os.path.splitext(pdf_files[0])[0]

def collect_first_level_subdirectories(directory):
    subdirectories = [os.path.join(directory, entry) for entry in os.listdir(directory) if os.path.isdir(os.path.join(directory, entry))]
    return subdirectories

def move_subfolders_up(target_directory):
    for root, dirs, files in os.walk(target_directory):
        for dir_name in dirs:
            top_lvl_folder = os.path.join(root, dir_name)
            sub_folders = [os.path.join(top_lvl_folder, subfolder) for subfolder in os.listdir(top_lvl_folder) if os.path.isdir(os.path.join(top_lvl_folder, subfolder))]

            if sub_folders:
                for sub_folder in sub_folders:
                    for item in os.listdir(sub_folder):
                        source = os.path.join(sub_folder, item)
                        base_name, file_extension = os.path.splitext(item)
                        new_item_name = f"{base_name}_supp{file_extension}"
                        destination = os.path.join(top_lvl_folder, new_item_name)
                        shutil.move(source, destination)

                    shutil.rmtree(sub_folder)


def rename_subdirectories(subdirectories, folders_csv, start_number):
    with open(folders_csv, 'w', newline='', encoding='utf-8') as csv_file1:
        csv_writer = csv.writer(csv_file1)
        csv_writer.writerow(['PDF Name', 'UUID'])

        for index, subdir in enumerate(subdirectories):
            pdf_filename = get_pdf_filename(subdir)
            new_number = start_number + index
            new_name = f'GRAD_ETD{new_number:06d}'  
            os.rename(subdir, os.path.join(os.path.dirname(subdir), new_name))
            csv_writer.writerow([pdf_filename, new_name])

def rename_files_in_folders(root_directory):
    for folder_name, _, files in os.walk(root_directory):
        folder_base = os.path.basename(folder_name)
        suppfile_counter = 3
        file_counter = 1

        for file_name in files:
            file_base, file_extension = os.path.splitext(file_name)

            if "_supp" in file_base:
                new_file_name = f"{folder_base}_{'{:04d}a'.format(suppfile_counter)}{file_extension}"
                suppfile_counter += 1
            else:
                new_file_name = f"{folder_base}_{'{:04d}a'.format(file_counter)}{file_extension}"
                file_counter += 1

            old_path = os.path.join(folder_name, file_name)
            new_path = os.path.join(folder_name, new_file_name)

            os.rename(old_path, new_path)

# Function to merge and delete CSV files
def merge_and_delete_csv_files(folders_csv, xml_csv, merged_csv):
    try:
        df1 = pd.read_csv(folders_csv)
        df2 = pd.read_csv(xml_csv)

        merged_df = pd.concat([df1, df2], axis=1)

        merged_df.to_csv(merged_csv, index=False)

        os.remove(folders_csv)
        os.remove(xml_csv)

        print(f'Merged data saved to {merged_csv}')
        print(f'{folders_csv} and {xml_csv} deleted.')

        # Open the merged CSV file
        os.system(f'start excel {merged_csv}')
    except Exception as e:
        print(f"An error occurred: {str(e)}")

if __name__ == "__main__":
    root_directory = input('Enter directory path: ')
    start_number = int(input("Enter the starting UUID number: "))

    current_datetime = datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
    folders_csv = f'folders_csv_{current_datetime}.csv'
    xml_csv = f'xml_csv_{current_datetime}.csv'
    merged_csv = f'ETD_batch_metadata_{current_datetime}.csv'

    unzip(root_directory)
    move_subfolders_up(root_directory)
    first_level_subdirectories = collect_first_level_subdirectories(root_directory)
    rename_subdirectories(first_level_subdirectories, folders_csv, start_number)

    with open(xml_csv, 'a', newline='', encoding='utf-8') as csv_file2:
        csv_writer = csv.writer(csv_file2)
        csv_writer.writerow(['Last Name', 'Title', 'Year'])

        for dirpath, _, filenames in os.walk(root_directory):
            for filename in filenames:
                if filename.endswith('.xml'):  
                    xml_file_path = os.path.join(dirpath, filename)
                    info = extract_info(xml_file_path)
                    remove_elements_from_xml(xml_file_path)
                    csv_writer.writerow([*info])

    merge_and_delete_csv_files(folders_csv, xml_csv, merged_csv)
    rename_files_in_folders(root_directory)
    print("Process completed successfully.")

    subprocess.Popen(['start', 'excel', merged_csv], shell=True)
