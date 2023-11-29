import os
import zipfile

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

input_directory = input('Enter the input directory of folders to zip:')

output_directory = input('Enter the output directory: ')

for folder in os.listdir(input_directory):
    folder_path = os.path.join(input_directory, folder)
    if os.path.isdir(folder_path):
        create_zip_for_folder(folder_path, output_directory)

print("Zip files created successfully.")
