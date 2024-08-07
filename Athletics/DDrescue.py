import os
import subprocess

def run_ddrescue(command):
    try:
        result = subprocess.run(command, shell=True, check=True, capture_output=True, text=True)
        print(f"Command succeeded: {result.stdout}")
    except subprocess.CalledProcessError as e:
        print(f"Command failed: {e.stderr}")

def main():
    # Get user input for the disc number
    disc_number = input("Enter the disc number (e.g., 1): ")
    disc_number_formatted = f"{int(disc_number):06d}"  # Format the number to 6 digits with leading zeros
    
    # Define file names based on the convention
    base_name = f"A2020-04_disc{disc_number_formatted}"
    documents_folder = os.path.expanduser("~/Documents")
    target_folder = os.path.join(documents_folder, base_name)
    
    # Create the target directory if it does not exist
    os.makedirs(target_folder, exist_ok=True)
    
    output_file = os.path.join(target_folder, f"{base_name}.iso")
    map_file = os.path.join(target_folder, f"{base_name}.map")
    
    # Define ddrescue commands
    first_pass_command = f"ddrescue -nvb 512 /dev/sr0 {output_file} {map_file}"
    second_pass_command = f"ddrescue -dvr 3 -b 512 /dev/sr0 {output_file} {map_file}"
    
    # Run ddrescue commands
    print("Running first pass...")
    run_ddrescue(first_pass_command)
    
    print("Running second pass...")
    run_ddrescue(second_pass_command)

if __name__ == "__main__":
    main()
