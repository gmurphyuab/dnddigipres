import os
import csv
import tkinter as tk
from tkinter import filedialog


def rename_files(folder_path):
    total_counter = 1 

    for folder_name, _, files in os.walk(folder_path):
        folder_base = os.path.basename(folder_name)
        files_by_extension = {}

        # Sort files by extension and group them
        for file_name in files:
            file_base, file_extension = os.path.splitext(file_name)
            if file_extension not in files_by_extension:
                files_by_extension[file_extension] = []
            files_by_extension[file_extension].append(file_name)

        extension_preference = ['.wav', '.mkv', '.mp4', '.mp3' '.tif', '.tiff', '.pdf']

        # Rename files according to extension preference
        for ext in extension_preference:
            if ext in files_by_extension:
                files = sorted(files_by_extension[ext], key=lambda x: x.lower())  
                for file_name in files:
                    new_file_name = f"{folder_base}_{'{:04d}a'.format(total_counter)}{os.path.splitext(file_name)[1]}"
                    old_path = os.path.join(folder_name, file_name)
                    new_path = os.path.join(folder_name, new_file_name)
                    try:
                        os.rename(old_path, new_path)
                        print(f"Successfully renamed file '{file_name}' in folder '{folder_name}'")
                    except Exception as rename_error:
                        print(f"Error renaming file '{file_name}' in folder '{folder_name}': {rename_error}")
                    total_counter += 1  # Increment total counter for each file

        # Rename files not in the preference list
        for ext, files in files_by_extension.items():
            if ext not in extension_preference:
                files = sorted(files, key=lambda x: x.lower()) 
                for file_name in files:
                    new_file_name = f"{folder_base}_{'{:04d}a'.format(total_counter)}{os.path.splitext(file_name)[1]}"
                    old_path = os.path.join(folder_name, file_name)
                    new_path = os.path.join(folder_name, new_file_name)
                    try:
                        os.rename(old_path, new_path)
                        print(f"Successfully renamed file '{file_name}' in folder '{folder_name}'")
                    except Exception as rename_error:
                        print(f"Error renaming file '{file_name}' in folder '{folder_name}': {rename_error}")
                    total_counter += 1  

def rename_folders_from_csv(csv_file_path):
    script_directory = os.path.dirname(os.path.abspath(__file__))
    csv_file_path = os.path.join(script_directory, csv_file_path)

    with open(csv_file_path, 'r') as csv_file:
        csv_reader = csv.reader(csv_file)
        next(csv_reader)

        for row in csv_reader:
            if len(row) == 3:
                folder_path, existing_name, new_name = row

                full_path = os.path.join(folder_path, existing_name)

                if os.path.exists(full_path):
                    new_full_path = os.path.join(folder_path, new_name)
                    try:
                        os.rename(full_path, new_full_path)
                        print(f"Renamed '{existing_name}' to '{new_name}' in '{folder_path}'.")
                        rename_files(new_full_path)
                    except Exception as e:
                        print(f"Failed to rename '{existing_name}' to '{new_name}' in '{folder_path}': {str(e)}")
                else:
                    print(f"Folder '{existing_name}' in '{folder_path}' does not exist.")

def browse_for_csv():
    file_path = filedialog.askopenfilename(filetypes=[("CSV Files", "*.csv")])
    if file_path:
        csv_entry.delete(0, tk.END)
        csv_entry.insert(0, file_path)

root = tk.Tk()
root.title("Folder and File Renamer")

csv_label = tk.Label(root, text="Select CSV File:")
csv_label.pack()

csv_entry = tk.Entry(root, width=50)
csv_entry.pack()

browse_button = tk.Button(root, text="Browse", command=browse_for_csv)
browse_button.pack()

rename_button = tk.Button(root, text="Rename Folders and Files", command=lambda: rename_folders_from_csv(csv_entry.get()))
rename_button.pack()

root.mainloop()
