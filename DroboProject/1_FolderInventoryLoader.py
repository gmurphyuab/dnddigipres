import os
import csv
from datetime import datetime
import subprocess

def create_inventory_csv(directory, csv_writer):
    items = os.listdir(directory)
    sorted_data = sorted(items, key=lambda x: int(''.join(filter(str.isdigit, x))))
    for item in sorted_data:
        item_path = os.path.join(directory, item)
        if os.path.isdir(item_path):
            csv_writer.writerow([directory, item])

def main():

    starting_directory = input('Enter the path to the directory: ')
    current_datetime = datetime.now().strftime('%Y%m%d_%H%M%S')
    csv_filename = f'Folder_inventory_{current_datetime}.csv'

    with open(csv_filename, mode='w', newline='') as csv_file:
        csv_writer = csv.writer(csv_file)
        csv_writer.writerow(['Directory Path', 'Folder Name', 'UUID'])
        create_inventory_csv(starting_directory, csv_writer)

    print(f"CSV file '{csv_filename}' has been created with directory paths and folder names.")
    subprocess.Popen(['start', 'excel', csv_filename], shell=True)

if __name__ == "__main__":
    main()

