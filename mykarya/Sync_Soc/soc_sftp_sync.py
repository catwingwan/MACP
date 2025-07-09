import os
import shutil
import logging
import sys

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
                            society_code = '_'.join(parts[:2])
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
        
        # Write files.txt
        with open('files.txt', 'w') as f:
            f.writelines(file_paths)
            print(f"Wrote {len(file_paths)} file paths to files.txt")
        
        # Write directories.txt
        with open('directories.txt', 'w') as d:
            d.writelines(dir_paths)
            print(f"Wrote {len(dir_paths)} directory paths to directories.txt")
        
        # Read the existing societies from Roy file
        roy_societies = set()
        roy_filename = f'Roy_{dist_period}S.txt'
        if os.path.exists(roy_filename):
            with open(roy_filename, 'r') as f:
                for line in f:
                    # Extract society code from Roy_XXXXXS.txt format
                    if '_' in line:
                        code = line.split('_')[0].strip()
                        roy_societies.add(code)
        
        # Create filtered output file with dist_period in name
        output_filename = f'02_{dist_period}_mkdir_soc_fdr.sh'
        with open(output_filename, 'w') as f:
            count = 0
            with open(roy_filename, 'r') as roy_file:
                for line in roy_file:
                    if '_' in line:
                        # Extract society code (ABRAMUS from ABRAMUS_20250327)
                        roy_society = line.split('_')[0].strip()
                        # Find matching society in our codes
                        for code in society_codes:
                            if roy_society in code:
                                f.write(f'mkdir "//volume1/{code.strip()}/downloads/{soc_dir}"\n')
                                count += 1
                                break
            print(f"Wrote {count} filtered mkdir commands to filtered_society_commands.txt")

        # Also keep original society_codes.txt
        with open('society_codes.txt', 'w') as s:
            for code in sorted(society_codes):
                s.write(f'mkdir "//volume1/{code.strip()}/downloads/{soc_dir}"\n')
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
def create_nas_cp_commands_file(dist_period):
    """Create .sh file with cp commands to NAS location"""
    try:
        output_filename = f'01_{dist_period}S_cp_to_nas.sh'
        
        with open('files.txt', 'r') as infile, open(output_filename, 'w') as outfile:
            count = 0
            for line in infile:
                line = line.strip()
                if line:
                    # Extract full path components
                    path_parts = line.split('\\')
                    if len(path_parts) >= 5:  # Ensure we have complete path
                        filename = path_parts[-1]
                        folder = path_parts[-2]  # ABRAMUS_201_D222_CRD
                        
                        # Transform folder name (ABRAMUS_201_D222_CRD -> ABRAMUS_201_L17U_CRD)
                        folder_parts = folder.split('_')
                        if len(folder_parts) >= 3:
                            target_folder = f"{folder_parts[0]}_{folder_parts[1]}_{folder_parts[2]}_{folder_parts[3]}"
                        else:
                            target_folder = folder
                        
                        # Build NAS destination path
                        nas_path = f'//volume1/NAS/Societies/{dist_period}/{target_folder}/{filename}'
                        
                        # Build cp command
                        cmd = f"cp '{line}' '{nas_path}'\n"
                        outfile.write(cmd)
                        count += 1
            
            print(f"Wrote {count} NAS cp commands to {output_filename}")
        return True
        
    except Exception as e:
        print(f"Error creating NAS cp commands: {str(e)}")
        return False


# Function to generate cp commands from files.txt filtered by Roy file
def create_cp_commands_file(dist_period, soc_dir):
    """Create .sh file with cp commands filtered by Roy_*S.txt
    
    Reads source files from {dist_period}.txt instead of files.txt
    """
    try:
        # Read society codes from Roy file
        roy_societies = set()
        roy_filename = f'Roy_{dist_period}S.txt'
        if os.path.exists(roy_filename):
            with open(roy_filename, 'r') as roy_file:
                for line in roy_file:
                    if '_' in line:
                        # Extract society code (ABRAMUS from ABRAMUS_20250327)
                        roy_society = line.split('_')[0].strip()
                        roy_societies.add(roy_society)

        # Create output file matching Roy filename pattern
        output_filename = f'03_{dist_period}S_cp_soc_files.sh'
        
        # Generate cp commands only for societies in Roy file
        source_filename = f'{dist_period}.txt'
        roy_filename = f'Roy_{dist_period}S.txt'
        
        print(f"Checking input files:")
        print(f"- Source file: {source_filename} exists: {os.path.exists(source_filename)}")
        print(f"- Roy file: {roy_filename} exists: {os.path.exists(roy_filename)}")
        
        if not os.path.exists(source_filename):
            print(f"Error: Source file {source_filename} not found")
            return False
        if not os.path.exists(roy_filename):
            print(f"Error: Roy file {roy_filename} not found")
            return False
            
        print("Files found, processing...")
        with open(source_filename, 'r') as infile, open(output_filename, 'w') as outfile:
            count = 0
            for line in infile:
                line = line.strip()
                if line:
                    # Extract filename and path components
                    path_parts = line.split('/')
                    if len(path_parts) >= 4:  # Ensure we have enough path components
                        filename = path_parts[-1]
                        # Get society from path like //volumn1/NAS/Societies/202503/ABRAMUS_201_L17U_CRD/
                        folder = path_parts[-2] if len(path_parts) >= 2 else ''
                        society_parts = folder.split('_') if '_' in folder else []
                        # Extract society code in format matching Roy file (e.g. "ABRAMUS" from "ABRAMUS_201_L17U_CRD")
                        society = society_parts[0] if society_parts and len(society_parts) >= 1 else ''
                        
                        # Only write command if society is in Roy file
                        if society:
                            print(f"Found society: {society} (from path: {line})")
                            if society in roy_societies:
                                print(f"Matched society in Roy file: {society}")
                                # Keep original path format with forward slashes
                                win_path = line.strip()
                                # Use full society folder name (e.g. ABRAMUS_201) in destination
                                full_society = '_'.join(society_parts[:2]) if len(society_parts) >= 2 else society
                                cmd = f"cp '{win_path}' '//volume1/{full_society}/downloads/{soc_dir}/'\n"
                                outfile.write(cmd)
                                count += 1
                            else:
                                print(f"Society not in Roy file: {society}")
                        else:
                            print(f"No society found in path: {line}")
            
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
