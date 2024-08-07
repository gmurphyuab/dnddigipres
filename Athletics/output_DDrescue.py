import os
import subprocess

def run_ddrescue(command):
    try:
        process = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        # Read and print the output and error streams line by line in real-time
        for stdout_line in iter(process.stdout.readline, ''):
            print(stdout_line, end='')
        for stderr_line in iter(process.stderr.readline, ''):
            print(stderr_line, end='')
        process.stdout.close()
        process.stderr.close()
        process.wait()
    except subprocess.CalledProcessError as e:
        print(f"Command failed with error: {e}")

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
