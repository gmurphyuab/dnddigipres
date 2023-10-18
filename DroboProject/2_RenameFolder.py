import os
import csv
import tkinter as tk
from tkinter import filedialog

# Function to rename folders based on CSV data
def rename_folders_from_csv(csv_file_path):
    with open(csv_file_path, 'r') as csv_file:
        csv_reader = csv.reader(csv_file)
        next(csv_reader)  # Skip the header row if present

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
                    except Exception as e:
                        result_label.config(text=f"Failed to rename '{existing_name}' to '{new_name}' in '{folder_path}': {str(e)}")
                else:
                    result_label.config(text=f"Folder '{existing_name}' in '{folder_path}' does not exist.")

# Function to browse for a CSV file
def browse_for_csv():
    file_path = filedialog.askopenfilename(filetypes=[("CSV Files", "*.csv")])
    if file_path:
        csv_entry.delete(0, tk.END)
        csv_entry.insert(0, file_path)

# Create the main window
root = tk.Tk()
root.title("Folder Renamer")

# Create and configure the label for CSV file selection
csv_label = tk.Label(root, text="Select CSV File:")
csv_label.pack()

# Create and configure the entry field for CSV file path
csv_entry = tk.Entry(root, width=50)
csv_entry.pack()

# Create and configure the Browse button
browse_button = tk.Button(root, text="Browse", command=browse_for_csv)
browse_button.pack()

# Create and configure the Rename button
rename_button = tk.Button(root, text="Rename Folders", command=lambda: rename_folders_from_csv(csv_entry.get()))
rename_button.pack()

# Create and configure the result label
result_label = tk.Label(root, text="")
result_label.pack()

# Start the Tkinter main loop
root.mainloop()
