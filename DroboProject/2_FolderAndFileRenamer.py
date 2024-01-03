import os
import csv
import tkinter as tk
from tkinter import filedialog

def rename_folders_from_csv(csv_file_path):
    script_directory = os.path.dirname(os.path.abspath(__file__))
    csv_file_path = os.path.join(script_directory, csv_file_path)

    with open(csv_file_path, 'r') as csv_file:
        csv_reader = csv.reader(csv_file)
        next(csv_reader)  

        for row in csv_reader:
            if len(row) == 3:
                folder_path, existing_name, new_name = row

                # Construct the full path to the folder
                full_path = os.path.join(folder_path, existing_name)

                # Check if the folder exists before renaming
                if os.path.exists(full_path):
                    new_full_path = os.path.join(folder_path, new_name)
                    try:
                        os.rename(full_path, new_full_path)
                        result_label.config(text=f"Renamed '{existing_name}' to '{new_name}' in '{folder_path}'.")
                        
                        rename_files(new_full_path)
                        
                    except Exception as e:
                        result_label.config(text=f"Failed to rename '{existing_name}' to '{new_name}' in '{folder_path}': {str(e)}")
                else:
                    result_label.config(text=f"Folder '{existing_name}' in '{folder_path}' does not exist.")

def rename_files(folder_path):
    try:
        script_directory = os.path.dirname(os.path.abspath(__file__))
        csv_file_path = os.path.join(script_directory, f'{os.path.basename(folder_path)}_originalfiles.csv')
        
        with open(csv_file_path, 'w', newline='') as csvfile:
            csv_writer = csv.writer(csvfile)
            csv_writer.writerow(['Original File Name', 'New File Name'])

            for folder_name, _, files in os.walk(folder_path):
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
                        continue  

                print(f"Successfully renamed files in {folder_name}")

        print(f"CSV file '{csv_file_path}' created successfully.")

    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        raise

def browse_for_csv():
    file_path = filedialog.askopenfilename(filetypes=[("CSV Files", "*.csv")])
    if file_path:
        csv_entry.delete(0, tk.END)
        csv_entry.insert(0, file_path)

root = tk.Tk()
root.title("Folder and File Renamer")

# Label for CSV file selection
csv_label = tk.Label(root, text="Select CSV File:")
csv_label.pack()

# Entry field for CSV file path
csv_entry = tk.Entry(root, width=50)
csv_entry.pack()

# Browse button
browse_button = tk.Button(root, text="Browse", command=browse_for_csv)
browse_button.pack()

# Rename button
rename_button = tk.Button(root, text="Rename Folders and Files", command=lambda: rename_folders_from_csv(csv_entry.get()))
rename_button.pack()

# Result label
result_label = tk.Label(root, text="")
result_label.pack()

root.mainloop()
