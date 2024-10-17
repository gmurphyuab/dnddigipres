import os
import tarfile
import subprocess
import platform
from datetime import datetime

def generate_virtual_tar_tree(input_directory):

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    output_file = f"qc_tar_{timestamp}.txt"
    
    # Open the output file in write mode
    with open(output_file, 'w') as out_file:
        
        # Loop through the input directory for .tar files
        for file_name in os.listdir(input_directory):
            if file_name.endswith('.tar'):
                file_path = os.path.join(input_directory, file_name)
                
                # Open the tar file and inspect its contents
                with tarfile.open(file_path) as tar:
                    
                    # Write the tar file name as a header in the output file
                    out_file.write(f"Directory tree for {file_name}:\n")
                    out_file.write("=" * (len(file_name) + 19) + "\n\n")
                    
                    # Create a dictionary-like structure of tar contents
                    virtual_tree = {}
                    
                    # Iterate through tar members to create a virtual file structure
                    for member in tar.getmembers():
                        path = member.name
                        # Break the path into parts (directories and files)
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
                    
    print(f"Directory trees of tar files have been saved to {output_file}.")
    
    # Automatically open the output file after generation
    try:
        if platform.system() == 'Windows':
            subprocess.call(['start', output_file], shell=True)
        elif platform.system() == 'Darwin':  # macOS
            subprocess.call(['open', output_file])
        else:  # Linux
            subprocess.call(['xdg-open', output_file])
    except Exception as e:
        print(f"Failed to open the file automatically: {e}")


if __name__ == "__main__":
    input_directory = input("Enter the directory containing tar files: ")
    generate_virtual_tar_tree(input_directory)
