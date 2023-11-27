import os
import csv
from datetime import datetime
import subprocess

# Specify the directory to start walking from
starting_directory = input('Enter the path to the directory: ')

# Get the current date and year
current_datetime = datetime.now().strftime('%Y%m%d_%H%M%S')

# Create a CSV file name with the current day and year
csv_filename = f'Folder_inventory_{current_datetime}.csv'

# Function to walk through the directory and write to CSV
def walk_directory_and_write_to_csv(directory, csv_writer):
    for root, dirs, _ in os.walk(directory):
        for folder_name in dirs:
            # Construct the full path of the folder
            folder_path = os.path.join(root, folder_name)
            
            # Write the directory path and folder name to the CSV
            csv_writer.writerow([root, folder_name])

# Open the CSV file for writing
with open(csv_filename, mode='w', newline='') as csv_file:
    csv_writer = csv.writer(csv_file)
    
    # Write headers to the CSV file
    csv_writer.writerow(['Directory Path', 'Folder Name', 'UUID'])
    
    # Walk through the directory and write to CSV
    walk_directory_and_write_to_csv(starting_directory, csv_writer)

# Read the CSV file and sort the data numerically based on the "Volume" column
with open(csv_filename, mode='r') as csv_file:
    csv_reader = csv.reader(csv_file)
    
    # Skip the header
    header = next(csv_reader)
    
    # Sort the data based on the numeric part of the "Volume" column
    sorted_data = sorted(csv_reader, key=lambda x: int(''.join(filter(str.isdigit, x[1]))))
    
# Write the sorted data back to the CSV file
with open(csv_filename, mode='w', newline='') as csv_file:
    csv_writer = csv.writer(csv_file)
    
    # Write headers to the CSV file
    csv_writer.writerow(header)
    
    # Write the sorted data
    csv_writer.writerows(sorted_data)

print(f"CSV file '{csv_filename}' has been created with directory paths and folder names, numerically sorted as desired.")

subprocess.Popen(['start', 'excel', csv_filename], shell=True)