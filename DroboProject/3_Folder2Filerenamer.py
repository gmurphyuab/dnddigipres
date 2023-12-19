import os
import csv

def rename_files_in_folders(root_folder):
    try:
        csv_file_path = f'{root_folder}_originalfiles.csv'
        with open(csv_file_path, 'w', newline='') as csvfile:
            csv_writer = csv.writer(csvfile)
            csv_writer.writerow(['Original File Name', 'New File Name'])

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

                    try:
                        os.rename(old_path, new_path)
                        csv_writer.writerow([file_name, new_file_name])
                    except Exception as rename_error:
                        print(f"Error renaming file '{file_name}' in folder '{folder_name}': {rename_error}")
                        continue  # Continue to the next file in case of an error

                print(f"Successfully renamed files in {folder_name}")

        print(f"CSV file '{csv_file_path}' created successfully.")

    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        raise

if __name__ == "__main__":
    try:
        root_folder = input('Enter the path to the directory: ')

        if not os.path.exists(root_folder) or not os.path.isdir(root_folder):
            raise FileNotFoundError(f"The specified directory '{root_folder}' does not exist.")

        rename_files_in_folders(root_folder)
        print("File renaming completed successfully.")

    except Exception as main_error:
        print(f"An unexpected error occurred: {main_error}")
