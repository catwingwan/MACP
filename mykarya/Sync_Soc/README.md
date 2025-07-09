# soc_sftp_sync_v2.py

## Description
This Python script automates the processing of distribution files for societies. It handles directory preparation, copying files based on specific folder patterns, generating detailed file and directory lists, creating path translation files, and generating NAS copy commands and shell scripts for file synchronization. The script is designed to facilitate efficient file management and transfer to NAS storage for society distribution periods.

## Prerequisites
- Python 3.x installed on your system.
- A `.env` file located in the same directory as the script containing the following variables:
  - `NAS_PATH` - The network path to the NAS.
  - `NAS_USER` - The username for NAS authentication.
  - `NAS_PASS` - The password for NAS authentication.

## Usage
Run the script using Python:

```bash
python soc_sftp_sync_v2.py
```

The script will prompt for the following inputs:
- **Distribution Period:** A string representing the distribution period (e.g., `202503`).
- **Distribution Directory:** The name of the distribution directory (e.g., `Mar_2025#`).

## Main Functions and Workflow

- `get_distribution_info()`: Prompts the user to input the distribution period and directory.
- `prepare_directories(source_dir, dist_period, destination_dir)`: Prepares source and destination directories for file operations.
- `copy_files_from_subfolder(sur_dir, des_dir, subfolder_pattern)`: Copies files from source to destination based on folder name patterns.
- `list_files_in_directory(directory, dist_period, soc_dir)`: Lists files and directories, extracts society codes, and generates related output files.
- `create_path_translation_file(dist_period)`: Creates a translated path file for NAS compatibility.
- `create_nas_cp_commands_file(dist_period)`: Generates a Windows batch file with NAS connection and copy commands.
- `create_cp_commands_file(dist_period, soc_dir)`: Generates a shell script with copy commands for society files.
- `execute_processing_steps(dist_period, soc_dir)`: Executes all processing steps in sequence.
- `log_completion(success)`: Logs the final status of the processing.

The script executes these steps sequentially to ensure proper file synchronization and command generation.

## Output Files

- `Roy_{dist_period}S.txt`: Contains full file paths from the source distribution folder.
- `directories.txt`: Lists directory paths with society codes for NAS folder structure.
- `society_codes.txt`: Contains NAS mkdir commands for society directories.
- `01_{dist_period}S_cp_to_nas.bat`: Windows batch file to connect to NAS, copy files, and disconnect.
- `02_{dist_period}_mkdir_soc_fdr.sh`: Shell script with mkdir commands for society folders.
- `03_{dist_period}S_cp_soc_files.sh`: Shell script with copy commands for society files.
- `{dist_period}.txt`: Translated file paths for NAS compatibility.

## Environment Variables

The script reads NAS connection details from a `.env` file. Ensure the file contains:

```
NAS_PATH=your_nas_path
NAS_USER=your_username
NAS_PASS=your_password
```

These are used to generate the NAS connection commands in the batch file.

## Logging and Error Handling

- The script uses Python's `logging` module to log informational messages and errors.
- Detailed print statements provide step-by-step feedback during execution.
- Errors during directory creation, file copying, or command generation are caught and reported.

---

This script streamlines the process of preparing and synchronizing society distribution files with NAS storage, improving efficiency and reducing manual effort.
