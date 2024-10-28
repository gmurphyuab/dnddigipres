import os
import tarfile
import subprocess
import platform
from datetime import datetime

def generate_virtual_tar_tree_for_subdirectories(top_level_directory):
    output_files = []  # Keep track of created output files

    # Loop through each subdirectory in the top-level directory
    for subdir in os.listdir(top_level_directory):
        subdir_path = os.path.join(top_level_directory, subdir)
        
        # Process only subdirectories
        if os.path.isdir(subdir_path):
            
            # Check if there are any .tar files in the subdirectory
            tar_files = [file_name for file_name in os.listdir(subdir_path) if file_name.endswith('.tar')]
            
            # Skip this subdirectory if there are no .tar files
            if not tar_files:
                continue
            
            # Generate a timestamped output file for each subdirectory
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_file = f"qc_tar_{subdir}_{timestamp}.txt"
            output_files.append(output_file)  # Add to the list of output files
            
            # Open the output file in write mode
            with open(output_file, 'w') as out_file:
                
                # Loop through the .tar files
                for file_name in tar_files:
                    file_path = os.path.join(subdir_path, file_name)
                    
                    # Open the tar file and inspect its contents with error handling
                    try:
                        with tarfile.open(file_path) as tar:
                            
                            # Write the tar file name as a header in the output file
                            out_file.write(f"Directory tree for {file_name}:\n")
                            out_file.write("=" * (len(file_name) + 19) + "\n\n")
                            
                            # Create a dictionary-like structure of tar contents
                            virtual_tree = {}
                            
                            # Iterate through tar members to create a virtual file structure
                            for member in tar.getmembers():
                                path = member.name
                                parts = path.split('/')
                                
                                # Insert the path into the virtual tree structure
                                current_level = virtual_tree
                                for part in parts:
                                    if part not in current_level:
                                        current_level[part] = {}
                                    current_level = current_level[part]
                            
                            # Function to print the virtual tree recursively
                            def print_virtual_tree(level, indent="", file=None):
                                for key in sorted(level):
                                    if len(level[key]) > 0:  # It's a directory
                                        out_file.write(f"{indent}{key}/\n")
                                        print_virtual_tree(level[key], indent + "    ", file)
                                    else:  # It's a file
                                        out_file.write(f"{indent}{key}\n")
                            
                            # Print the virtual tree to the output file
                            print_virtual_tree(virtual_tree, file=out_file)
                            
                            # Separate each tar file tree in the output file
                            out_file.write("\n\n")
                    
                    except tarfile.ReadError:
                        print(f"Error reading {file_name}. Skipping this file due to unexpected end of data.")
                        continue  # Skip to the next .tar file
            
            print(f"Directory tree for {subdir} saved to {output_file}.")
            
            # Automatically open the output file after generation
            try:
                if platform.system() == 'Windows':
                    subprocess.call(['start', output_file], shell=True)
                elif platform.system() == 'Darwin':  # macOS
                    subprocess.call(['open', output_file])
                else:  # Linux
                    subprocess.call(['xdg-open', output_file])
            except Exception as e:
                print(f"Failed to open {output_file} automatically: {e}")

    # Prompt to delete all created output files
    delete_output_files(output_files)

def delete_output_files(output_files):
    user_confirmation = input("Do you want to delete all generated text files? (yes/no): ").strip().lower()
    if user_confirmation.strip().lower() in ['yes', 'y']:
        for file in output_files:
            try:
                os.remove(file)
                print(f"Deleted {file}")
            except Exception as e:
                print(f"Failed to delete {file}: {e}")
    else:
        print("No files were deleted.")

if __name__ == "__main__":
    top_level_directory = input("Enter the top-level directory containing subdirectories of tar files: ")
    generate_virtual_tar_tree_for_subdirectories(top_level_directory)
