import os
import shutil
import logging
import sys

# Additional import for .env parsing
from pathlib import Path

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Function to get distribution period and directory details from user
def get_distribution_info():
    dist_period = input('Distribution Period: ')  # e.g., 202503
    soc_dir = input('Distribution directory: ')  # e.g., Mar_2025#
    return dist_period, soc_dir

# Example of Improved mkdir function error handling.
def prepare_directories(source_dir, dist_period, destination_dir):
    sur_dir = os.path.join(source_dir, dist_period)
    des_dir = os.path.join(destination_dir, dist_period)

    print(f'Looking for files in: {sur_dir}')
    print(f'Output will be in: {des_dir}')

    if not os.path.exists(sur_dir):
        print(f'Source directory does not exist: {sur_dir}')
        return None, None

    try:
        os.makedirs(des_dir, exist_ok=True)
        print(f'Destination directory created: {des_dir}')
    except Exception as e:
        print(f'Error creating destination directory {des_dir}: {e}')
        return None, None

    return sur_dir, des_dir

def copy_files_from_subfolder(sur_dir, des_dir, subfolder_pattern):
    """
    Enhanced folder copy with detailed debugging output.
    Returns tuple: (success: bool, files_copied: int, error: str)
    """
    try:
        # Input validation
        print(f"\nStarting copy operation:")
        print(f"Source: {sur_dir}")
        print(f"Destination: {des_dir}")
        print(f"Pattern: {subfolder_pattern}")
        
        if not os.path.exists(sur_dir):
            return False, 0, f"Source directory not found: {sur_dir}"
            
        if isinstance(subfolder_pattern, str):
            subfolder_pattern = [subfolder_pattern]
            
        file_count = 0
        matched_folders = 0
        
        for root, _, files in os.walk(sur_dir):
            print(f"\nScanning: {root}")
            print(f"Files found: {len(files)}")
            
            # Check if there are files before processing patterns
            if len(files) == 0:
                print(f"No files found in {root}, skipping destination creation.")
                continue
            
            for pattern in subfolder_pattern:
                # Normalize path and pattern for consistent comparison
                normalized_path = os.path.normpath(root).replace('\\', '/')
                path_parts = [p for p in normalized_path.split('/') if p]
                
                # Check if pattern matches any complete path component
                pattern_matched = False
                pattern_index = -1
                
                for i, part in enumerate(path_parts):
                    # Match either exact folder name or folder name containing pattern
                    if pattern.lower() == part.lower() or pattern.lower() in part.lower():
                        pattern_matched = True
                        pattern_index = i
                        break
                
                if pattern_matched:
                    print(f"Exact folder match for pattern '{pattern}' at position {pattern_index}")
                    # Get just the last folder in the path (ABRAMUS_201_L21U_CRD)
                    last_folder = path_parts[-1]
                    dest_path = os.path.join(des_dir, last_folder)
                    
                    print(f"Source path components: {path_parts}")
                    print(f"Matched pattern at index: {pattern_index}")
                    print(f"Full destination path: {dest_path}")
                    
                    print(f"Creating destination: {dest_path}")
                    os.makedirs(dest_path, exist_ok=True)
                    
                    for file in files:
                        src_file = os.path.join(root, file)
                        dst_file = os.path.join(dest_path, file)
                        print(f"Attempting copy: {src_file} -> {dst_file}")
                        
                        try:
                            shutil.copy2(src_file, dst_file)
                            file_count += 1
                            print("Copy successful")
                        except Exception as e:
                            print(f"Copy failed: {str(e)}")
                            continue
                            
                    # After copying files, check if destination folder is empty or contains only empty files and delete if so
                    if os.path.exists(dest_path):
                        try:
                            # List all files in the destination folder
                            files_in_dest = [os.path.join(dest_path, f) for f in os.listdir(dest_path) if os.path.isfile(os.path.join(dest_path, f))]
                            # Check if all files are empty (size 0)
                            all_empty = all(os.path.getsize(f) == 0 for f in files_in_dest) if files_in_dest else True
                            if all_empty:
                                # Delete all empty files
                                for f in files_in_dest:
                                    os.remove(f)
                                    print(f"Deleted empty file: {f}")
                                # Delete the folder
                                os.rmdir(dest_path)
                                print(f"Deleted empty destination folder: {dest_path}")
                        except Exception as e:
                            print(f"Failed to delete empty folder or files in {dest_path}: {str(e)}")
                    matched_folders += 1
                else:
                    print(f"Pattern '{pattern}' not found as complete folder in path")
        
        print(f"\nOperation complete. Folders matched: {matched_folders}, Files copied: {file_count}")
        return True, file_count, ""
        
    except Exception as e:
        error_msg = f"Fatal error: {str(e)}"
        print(error_msg)
        return False, file_count, error_msg

          
# Function to list files matching certain criteria and write to 'directories.txt'
def list_files_in_directory(directory, dist_period, soc_dir):
    """List all files, directories, and extract society codes"""
    if not os.path.exists(directory):
        print(f"Error: The directory '{directory}' does not exist.")
        return False

    try:
        # Prepare output containers
        file_paths = []
        dir_paths = []
        society_codes = set()  # Using set to avoid duplicates
        
        # Walk through directory tree
        for root, dirs, files in os.walk(directory):
            # Add directory paths with society codes
            for d in dirs:
                full_path = os.path.join(root, d)
                dir_path = full_path + '\t'
                
                # Extract society code if pattern matches
                if '_' in d and 'CRD' in d:
                    try:
                        parts = d.split('_')
                        if len(parts) >= 3:  # Ensure format is XXX_XXX_XXX
                            society_code = parts[0] + "_" + parts[1] + "  " + parts[2]
                            dir_path += society_code
                    except:
                        pass
                
                dir_paths.append(dir_path + '\n')
            
            # Add file paths and extract society codes
            for f in files:
                file_paths.append(os.path.join(root, f) + '\n')
            
            # Extract society code from current directory path
            folder_parts = root.split('\\')
            for folder in folder_parts:
                if '_' in folder and 'CRD' in folder:
                    try:
                        parts = folder.split('_')
                        if len(parts) >= 3:  # Ensure format is XXX_XXX_XXX
                            society_code = '_'.join(parts[:2])
                            society_codes.add(society_code + '\n')
                    except:
                        continue
        
        # Write Roy file instead of files.txt
        roy_filename = f'Roy_{dist_period}S.txt'
        with open(roy_filename, 'w') as f:
            f.writelines(file_paths)
            print(f"Wrote {len(file_paths)} file paths to {roy_filename}")
        
        # Read roy_lines once for reuse
        with open(roy_filename, 'r') as roy_file:
            roy_lines = roy_file.readlines()
        
        # Write directories.txt with multiple folder parts per society code
        with open('directories.txt', 'w') as d:
            count_dirs = 0
            for code in society_codes:
                folder_parts_set = set()
                for line in roy_lines:
                    if code.strip() in line:
                        parts = line.strip().split(os.sep)
                        for part in parts:
                            if '_CRD' in part:
                                parts_split = part.split('_')
                                if len(parts_split) >= 3:
                                    folder_parts_set.add(parts_split[2])
                for folder_part in folder_parts_set:
                    dir_path = f"//volume1/{code.strip()}/downloads/{soc_dir}/CRD/{folder_part}\n"
                    d.write(dir_path)
                    count_dirs += 1
            print(f"Wrote {count_dirs} directory paths to directories.txt")
        
        # Create filtered output file with dist_period in name
        output_filename = f'02_{dist_period}_mkdir_soc_fdr.sh'
        with open(output_filename, 'w') as f:
            count = 0
            roy_societies = set()
            for line in roy_lines:
                if '_' in line:
                    # Extract society code (ABRAMUS_201 from ABRAMUS_201_L17U_CRD)
                    parts = line.strip().split(os.sep)
                    roy_society = ''
                    roy_society_1 = parts[2]
                    for part in parts:
                        if '_CRD' in part:
                            roy_society = '_'.join(part.split('_')[:2])
                            roy_society_1 = part.split('_')[:3]
                            break
                    if roy_society:
                        roy_societies.add(roy_society)
            for code in society_codes:
                for roy_society in roy_societies:
                    if roy_society in code:
                        # Collect all folder parts for this society code from filtered lines only
                        folder_parts_set = set()
                        filtered_lines = [line for line in roy_lines if roy_society in line]
                        for line in filtered_lines:
                            parts = line.strip().split(os.sep)
                            for part in parts:
                                if '_CRD' in part:
                                    parts_split = part.split('_')
                                    if len(parts_split) >= 3:
                                        folder_parts_set.add(parts_split[2])
                        for folder_part in folder_parts_set:
                            print(f'Writing mkdir command: mkdir -p "//volume1/{code.strip()}/downloads/{soc_dir}/CRD/{folder_part}"')
                            f.write(f'mkdir -p "//volume1/{code.strip()}/downloads/{soc_dir}/CRD/{folder_part}"\n')
                            count += 1
                        break
            print(f"Wrote {count} filtered mkdir commands to filtered_society_commands.txt")

        # Also keep original society_codes.txt
        with open('society_codes.txt', 'w') as s:
            for code in sorted(society_codes):
                s.write(f'mkdir -p "//volume1/{code.strip()}/downloads/{soc_dir}/CRD"\n')
            print(f"Wrote {len(society_codes)} mkdir commands to society_codes.txt")
        
        return True
        
    except Exception as e:
        print(f"Error processing directory: {str(e)}")
        return False

# Function to create path translation file
def create_path_translation_file(dist_period):
    """Create {dist_period}.txt with translated paths"""
    try:
        output_filename = f'{dist_period}.txt'
        
        with open('files.txt', 'r') as infile, open(output_filename, 'w') as outfile:
            count = 0
            for line in infile:
                line = line.strip()
                if line:
                    # Transform path
                    translated = line.replace('C:\\DIVA\\SOC\\', '//volume1/NAS/Societies/')
                    translated = translated.replace('\\', '/')
                    outfile.write(translated + '\n')
                    count += 1
            
            print(f"Wrote {count} translated paths to {output_filename}")
        return True
        
    except Exception as e:
        print(f"Error creating path translation file: {str(e)}")
        return False

# Function to generate NAS copy commands from files.txt
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

def create_nas_cp_commands_file(dist_period):
    """Create .bat file with net use connect, cp commands, and disconnect"""
    try:
        output_filename = f'01_{dist_period}S_cp_to_nas.bat'
        env_vars = read_env_variables()
        net_use_cmd = ''
        net_disconnect_cmd = ''
        if 'NAS_PATH' in env_vars and 'NAS_USER' in env_vars and 'NAS_PASS' in env_vars:
            net_use_cmd = f'net use N: \\\{env_vars["NAS_PATH"]}\\NAS {env_vars["NAS_PASS"]} /user:{env_vars["NAS_USER"]} \n'
            net_disconnect_cmd = 'net use N: /delete\n'
        else:
            print("Warning: NAS_PATH, NAS_USER or NAS_PASS not found in .env. Skipping net use commands.")
        
        with open(output_filename, 'w') as outfile:
            # Write net use connect command first if available
            if net_use_cmd:
                outfile.write(net_use_cmd)
            
            # Write xcopy command with dist_period variable
            source_path = f'C:\\DIVA\\SOC\\{dist_period}\\*.*'
            dest_path = f'n:\\Societies\\{dist_period}\\'
            cmd = f'xcopy /s /e "{source_path}" "{dest_path}"\n'
            outfile.write(cmd)
            
            # Write net use disconnect command at the end if available
            if net_disconnect_cmd:
                outfile.write(net_disconnect_cmd)
            
            print(f"Wrote NAS copy commands to {output_filename} with net use connect/disconnect and xcopy")
        return True
        
    except Exception as e:
        print(f"Error creating NAS cp commands: {str(e)}")
        return False


# Function to generate cp commands from files.txt filtered by Roy file
def create_cp_commands_file(dist_period, soc_dir):
    '''Create .sh file with cp commands based on source paths from {dist_period}.txt and destination using dist_period.'''
    try:
        source_filename = f'{dist_period}.txt'
        output_filename = f'03_{dist_period}S_cp_soc_files.sh'
        
        if not os.path.exists(source_filename):
            print(f"Error: Source file {source_filename} not found")
            return False
        
        count = 0
        
        with open(source_filename, 'r') as infile, open(output_filename, 'w') as outfile:
            lines = infile.readlines()
            
            # Extract society codes and folder parts from lines
            society_folder_map = {}
            for line in lines:
                line = line.strip()
                if line:
                    path_parts = line.split('/')
                    if len(path_parts) >= 4:
                        folder = path_parts[-2]
                        society_parts = folder.split('_')
                        if len(society_parts) >= 3:
                            society = '_'.join(society_parts[:2])
                            folder_part = society_parts[2]
                            if society not in society_folder_map:
                                society_folder_map[society] = set()
                            society_folder_map[society].add(folder_part)
            
            for society, folder_parts in society_folder_map.items():
                for folder_part in folder_parts:
                    dest_path = f"//volume1/{society}/downloads/{soc_dir}/CRD/{folder_part}/"
                    for line in lines:
                        if society in line and folder_part in line:
                            cp_cmd = f"cp -r '{line.strip()}' '{dest_path}'\n"
                            outfile.write(cp_cmd)
                            count += 1
            
            print(f"Wrote {count} cp commands to {output_filename}")
            return True
    
    except Exception as e:
        print(f"Error creating cp commands: {str(e)}")
        return False

# End function

def get_directory_paths():
    """Get source and destination directory paths
    
    Returns:
        tuple: (source_dir, destination_dir)
    """
    return "X:\\Dist_Reports\\CRD\\", "C:\\DIVA\\SOC\\"

def generate_roy_file(dist_period):
    """Generate Roy_{dist_period}S.txt file with full file paths from SOC\\{dist_period} folder"""
    # roy_folder = os.path.join("SOC", dist_period)
    roy_folder = dist_period
    roy_filename = f"Roy_{dist_period}S.txt"
    try:
        if not os.path.exists(roy_folder):
            print(f"Roy folder does not exist: {roy_folder}")
            return False
        with open(roy_filename, 'w') as roy_file:
            for root, _, files in os.walk(roy_folder):
                for file in files:
                    full_path = os.path.join(root, file)
                    roy_file.write(full_path + '\n')
        print(f"Generated {roy_filename} with full file paths from {roy_folder}")
        return True
    except Exception as e:
        print(f"Error generating {roy_filename}: {str(e)}")
        return False

def execute_processing_steps(dist_period, soc_dir):
    """Execute all processing steps in sequence
    
    Args:
        dist_period: Distribution period string
        soc_dir: Society directory name
        
    Returns:
        bool: True if all steps completed successfully
    """
    source_dir, destination_dir = get_directory_paths()
    sur_dir, des_dir = prepare_directories(source_dir, dist_period, destination_dir)
    if not sur_dir or not des_dir:
        return False

    # Generate Roy file before other steps
    if not generate_roy_file(dist_period):
        return False

    steps = [
        lambda: copy_files_from_subfolder(sur_dir, des_dir, ['SOC']),
        lambda: list_files_in_directory(des_dir, dist_period, soc_dir),
        lambda: create_path_translation_file(dist_period),
        lambda: create_nas_cp_commands_file(dist_period),
        lambda: create_cp_commands_file(dist_period, soc_dir)
    ]
    
    for step in steps:
        if not step():
            return False
    return True

def log_completion(success):
    """Log final processing status
    
    Args:
        success (bool): Whether processing succeeded
    """
    if success:
        print("Process completed successfully!")
    else:
        print("Process completed with errors")

def main():
    """Main entry point for the distribution processing"""
    try:
        dist_period, soc_dir = get_distribution_info()
        success = execute_processing_steps(dist_period, soc_dir)
        log_completion(success)
        return 0 if success else 1
    except Exception as e:
        logging.error(f"Fatal error: {str(e)}")
        return 1

if __name__ == "__main__":
    sys.exit(main())
