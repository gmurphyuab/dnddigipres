import os

def rename_files_in_folders(root_folder):
    for folder_name, _, files in os.walk(root_folder):
        folder_base = os.path.basename(folder_name)
        files.sort()
        file_counter = 1

        for file_name in files:
            file_base, file_extension = os.path.splitext(file_name)
            new_file_name = f"{folder_base}_{'{:04d}a'.format(file_counter)}{file_extension}"
            file_counter += 1

            old_path = os.path.join(folder_name, file_name)
            new_path = os.path.join(folder_name, new_file_name)

            os.rename(old_path, new_path)

if __name__ == "__main__":
    root_folder = input('Enter the path to the directory: ')
    rename_files_in_folders(root_folder)
