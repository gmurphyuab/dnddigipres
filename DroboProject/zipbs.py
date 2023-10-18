import os
import zipfile

# Function to create a zip file for a folder excluding .txt files
def create_zip_for_folder(folder_path, output_dir):
    folder_name = os.path.basename(folder_path)
    zip_filename = os.path.join(output_dir, f"{folder_name}.zip")

    with zipfile.ZipFile(zip_filename, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for root, dirs, files in os.walk(folder_path):
            for file in files:
                if not file.endswith('.txt'):
                    file_path = os.path.join(root, file)
                    arcname = os.path.relpath(file_path, folder_path)
                    zipf.write(file_path, arcname)

# Specify the input directory where the folders are located
input_directory = input('Enter the input directory to zip:')

# Specify the output directory where the zip files will be saved
output_directory = input('Enter the output directory: ')

# Iterate over folders in the input directory
for folder in os.listdir(input_directory):
    folder_path = os.path.join(input_directory, folder)
    if os.path.isdir(folder_path):
        create_zip_for_folder(folder_path, output_directory)

print("Zip files created successfully.")
