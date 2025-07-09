import os
import sys
from pathlib import Path
import shutil

def copy_files_exclude_folders(source_folder, destination_folder):
    """
    Copy all files from source_folder (including subdirectories) to destination_folder
    without recreating folder structure, excluding folders themselves.
    """
    if not os.path.exists(source_folder):
        print(f"Source folder does not exist: {source_folder}")
        return False, 0

    try:
        os.makedirs(destination_folder, exist_ok=True)
        file_count = 0
        for root, _, files in os.walk(source_folder):
            for file in files:
                src_file = os.path.join(root, file)
                dst_file = os.path.join(destination_folder, file)
                try:
                    shutil.copy2(src_file, dst_file)
                    file_count += 1
                    print(f"Copied: {src_file} -> {dst_file}")
                except Exception as e:
                    print(f"Failed to copy {src_file}: {str(e)}")
                    continue
        print(f"Total files copied: {file_count}")
        return True, file_count
    except Exception as e:
        print(f"Fatal error during copy: {str(e)}")
        return False, 0

def read_env_variables(env_path='.env'):
    """Read .env file and return a dictionary of variables"""
    env_vars = {}
    env_file = Path(env_path)
    if not env_file.exists():
        print(f".env file not found at {env_path}")
        return env_vars
    with env_file.open() as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith('#') and '=' in line:
                key, value = line.split('=', 1)
                env_vars[key.strip()] = value.strip()
    return env_vars

def create_nas_cp_commands_file(dist_period, destination_path):
    """
    Create a batch file named 01_copy_{dist_period}_nas.bat that:
    1. Connects to NAS using net use with credentials from .env
    2. Creates the dist_period directory on NAS if it does not exist
    3. Copies all files from destination_path to the NAS path
    4. Disconnects the net use connection
    """
    env_vars = read_env_variables()
    nas_path = env_vars.get('NAS_PATH')
    nas_user = env_vars.get('NAS_USER')
    nas_pass = env_vars.get('NAS_PASS')

    output_filename = f'01_copy_{dist_period}_nas.bat'

    if not nas_path or not nas_user or not nas_pass:
        print("NAS_PATH, NAS_USER, or NAS_PASS not found in .env file. Cannot create NAS batch file.")
        return False

    try:
        with open(output_filename, 'w') as f:
            # Connect to NAS
            net_use_cmd = f'net use N: \\\\{nas_path}\\NAS {nas_pass} /user:{nas_user}\n'
            f.write(net_use_cmd)
            # Create directory if not exists
            mkdir_cmd = f'if not exist N:\\Societies\\{dist_period} mkdir N:\\Societies\\{dist_period}\n'
            f.write(mkdir_cmd)
            # Copy files
            copy_cmd = f'xcopy /s /e /y "{destination_path}\\*" "N:\\Societies\\{dist_period}\\"\n'
            f.write(copy_cmd)
            # Disconnect
            net_disconnect_cmd = 'net use N: /delete\n'
            f.write(net_disconnect_cmd)

        print(f"Created NAS copy batch file: {output_filename}")
        return True
    except Exception as e:
        print(f"Error creating NAS copy batch file: {str(e)}")
        return False

def generate_file_list_and_script(dist_period, destination_path, soc_dir):
    """
    Generate a list of file names in destination_path saved as soc_statement.txt
    and generate a shell script 02_Sync_soc_{dist_period}.sh to copy files to
    \\volume1\{first_char_of_file_name}\downloads\{dist_period}\detail_statement\
    The shell script reads soc_statement.txt and creates cp commands with source and destination paths.
    """
    list_filename = 'soc_statement.txt'
    script_filename = f'02_Sync_soc_{dist_period}.sh'

    try:
        # Write file names to soc_statement.txt
        with open(list_filename, 'w') as list_file:
            for root, _, files in os.walk(destination_path):
                for file in files:
                    list_file.write(file + '\n')

        # Read soc_statement.txt and generate shell script
        with open(list_filename, 'r') as list_file, open(script_filename, 'w') as script_file:
            for line in list_file:
                file_name = line.strip()
                if not file_name:
                    continue
                parts = file_name.split('_')
                #society_code = parts[0] if parts else 'UNKNOWN'
                society_code = '_'.join(parts[:2])
                src_path = f"\\\\volume1\\NAS\\Societies\\{dist_period}\\{file_name}"
                dest_path = f"\\\\volume1\\{society_code}\\downloads\\{soc_dir}\\DETAILS_STATEMENT\\"
                cp_cmd = f"cp '{src_path}' '{dest_path}'\n"
                script_file.write(cp_cmd)

        print(f"Generated file list {list_filename} and script {script_filename}")
        return True
    except Exception as e:
        print(f"Error generating file list and script: {str(e)}")
        return False

def get_distribution_info():
    dist_period = input('Distribution Period: ')  # e.g., 202503
    soc_dir = input('Distribution directory: ')  # e.g., Mar_2025#
    source_folder = input('Source folder name (to append to Dist_Payment_No): ')  # e.g., 202503
    return dist_period, soc_dir, source_folder

def main():
    dist_period, soc_dir, source_folder = get_distribution_info()
    source_path = os.path.join("X:\\Dist_Reports\\Dist_Payment_No", source_folder, "SOCIETY_STATEMENT_PRINT_BANK_INFO")
    destination_path = os.path.join("C:\\DIVA\\SOC", source_folder)
    success, count = copy_files_exclude_folders(source_path, destination_path)
    if success:
        print(f"Successfully copied {count} files from {source_path} to {destination_path}")
        batch_success = create_nas_cp_commands_file(dist_period, destination_path)
        if batch_success:
            print("Batch file created successfully.")
            list_script_success = generate_file_list_and_script(dist_period, destination_path, soc_dir)
            if list_script_success:
                print("File list and sync script generated successfully.")
                return 0
            else:
                print("Failed to generate file list and sync script.")
                return 1
        else:
            print("Failed to create batch file.")
            return 1
    else:
        print("File copy failed.")
        return 1

if __name__ == "__main__":
    sys.exit(main())
