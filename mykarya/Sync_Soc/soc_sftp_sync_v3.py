import os
import sys
import shutil
import logging
from pathlib import Path

# ===== COMMON UTILITY =====
def read_env_variables(env_path='.env'):
    env_vars = {}
    env_file = Path(env_path)
    if env_file.exists():
        with env_file.open() as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#') and '=' in line:
                    key, value = line.split('=', 1)
                    env_vars[key.strip()] = value.strip()
    return env_vars

def validate_dist_period(dist_period, distribution_type):
    if distribution_type == 'PAYMENT' and not dist_period.endswith('S'):
        logging.error("For PAYMENT, dist_period must end with 'S' (e.g., 202506S).")
        return False
    if distribution_type == 'CRD' and dist_period.endswith('S'):
        logging.error("For CRD, dist_period should not end with 'S' (e.g., 202506).")
        return False
    return True

# ===== PAYMENT PIPELINE 01 =====
def payment_pipeline(dist_period, soc_dir):
    source_folder = os.path.join("X:\\Dist_Reports\\Dist_Payment_No", dist_period, "SOCIETY_STATEMENT_PRINT_BANK_INFO")
    destination_folder = os.path.join("C:\\DIVA\\SOC", soc_dir, "PAYMENT")
    
    if not os.path.exists(source_folder):
        logging.error(f"Source folder does not exist: {source_folder}")
        return
    os.makedirs(destination_folder, exist_ok=True)
    count = 0
    copied_files = []
    for root, _, files in os.walk(source_folder):
        for file in files:
            src = os.path.join(root, file)
            dst = os.path.join(destination_folder, file)
            try:
                shutil.copy2(src, dst)
                copied_files.append(file)
                count += 1
            except Exception as e:
                logging.warning(f"Failed to copy {src}: {e}")
    logging.info(f"Copied {count} files to {destination_folder}")

    # Export copied files list to payment.txt
    export_file = os.path.join(destination_folder, 'payment.txt')
    try:
        with open(export_file, 'w') as ef:
            for filename in copied_files:
                ef.write(filename + '\n')
        logging.info(f"Exported copied files list to {export_file}")
    except Exception as e:
        logging.error(f"Failed to write export file {export_file}: {e}")

    env_vars = read_env_variables()
    nas_path = env_vars.get('NAS_PATH')
    nas_user = env_vars.get('NAS_USER')
    nas_pass = env_vars.get('NAS_PASS')

    if not nas_path or not nas_user or not nas_pass:
        logging.error("NAS_PATH, NAS_USER, or NAS_PASS environment variables are missing.")
        return

    batch_dir = os.path.join(destination_folder, 'batch_files')
    os.makedirs(batch_dir, exist_ok=True)
    batch_file = os.path.join(batch_dir, f'PAYMENT_copy_{dist_period}_01.bat')
    with open(batch_file, 'w') as f:
        f.write(f'net use N: \\\\{nas_path}\\NAS {nas_pass} /user:{nas_user}\n')
        f.write(f'if not exist N:\\Societies\\{dist_period} mkdir N:\\Societies\\{dist_period}\n')
        f.write(f'xcopy /s /e /y "{destination_folder}\\*.pdf" "N:\\Societies\\{dist_period}\\"\n')
        f.write('net use N: /delete\n')
    logging.info(f"Created NAS batch: {batch_file}")

# ===== PAYMENT PIPELINE 02 =====
def payment_02_pipeline(dist_period, soc_dir):
    nas_base_path = f"//volume1/NAS/Societies/{dist_period}"
    export_file = os.path.join("C:\\DIVA\\SOC", soc_dir, 'PAYMENT', 'payment.txt')
    batch_dir = os.path.join("C:\\DIVA\\SOC", soc_dir, 'PAYMENT', 'batch_files')
    os.makedirs(batch_dir, exist_ok=True)
    batch_file = os.path.join(batch_dir, f'PAYMENT_copy_{dist_period}_02.sh')

    if not os.path.exists(export_file):
        logging.error(f"Export file does not exist: {export_file}")
        return

    try:
        with open(export_file, 'r') as ef, open(batch_file, 'w') as bf:
            bf.write("#!/bin/bash\n\n")
            created_dirs = set()
            for line in ef:
                filename = line.strip()
                parts = filename.split('_')
                if len(parts) >= 2:
                    folder_name = f"{parts[0]}_{parts[1]}"
                else:
                    folder_name = parts[0]
                destination_base = f"//volume1/{folder_name}/downloads/{soc_dir}/DETAILS_STATEMENT"
                src_file = os.path.join(nas_base_path, filename).replace('\\', '/')
                dst_file = os.path.join(destination_base, filename).replace('\\', '/')
                if destination_base not in created_dirs:
                    bf.write(f'mkdir -p "{destination_base}"\n')
                    created_dirs.add(destination_base)
                bf.write(f'cp "{src_file}" "{dst_file}"\n')
        logging.info(f"Created batch script: {batch_file}")
    except Exception as e:
        logging.error(f"Failed to create batch script in payment_02_pipeline: {e}")

# ===== CRD 01 PIPELINE (simplified) =====
def crd_pipeline(dist_period, soc_dir):
    source_folder = os.path.join("X:\\Dist_Reports\\CRD", dist_period + "\\ROY" + dist_period + "S", "SOCIETY")
    destination_folder = os.path.join("C:\\DIVA\\SOC", soc_dir)
    
    if not os.path.exists(source_folder):
        logging.error(f"Source folder does not exist: {source_folder}")
        return

    # List subfolders inside SOCIETY folder
    subfolders = [f for f in os.listdir(source_folder) if os.path.isdir(os.path.join(source_folder, f))]
    if not subfolders:
        logging.warning(f"No subfolders found inside {source_folder}")
    else:
        copied_full_paths = []
        for subfolder in subfolders:
            src_path = os.path.join(source_folder, subfolder)
            # List second-level subfolders inside each subfolder
            second_level_subfolders = [sf for sf in os.listdir(src_path) if os.path.isdir(os.path.join(src_path, sf))]
            if not second_level_subfolders:
                logging.warning(f"No second-level subfolders found inside {src_path}")
            else:
                for second_subfolder in second_level_subfolders:
                    src_sub_path = os.path.join(src_path, second_subfolder)
                    dst_sub_path = os.path.join(destination_folder, subfolder, second_subfolder)
                    try:
                        shutil.copytree(src_sub_path, dst_sub_path, dirs_exist_ok=True)
                        logging.info(f"Copied {src_sub_path} to {dst_sub_path}")
                        copied_full_paths.append(dst_sub_path)
                    except Exception as e:
                        logging.error(f"Failed to copy {src_sub_path} to {dst_sub_path}: {e}")

    # Export copied subfolders list to crd.txt
    copied_subfolders = []
    for subfolder in subfolders:
        src_path = os.path.join(source_folder, subfolder)
        second_level_subfolders = [sf for sf in os.listdir(src_path) if os.path.isdir(os.path.join(src_path, sf))]
        for second_subfolder in second_level_subfolders:
            copied_subfolders.append(os.path.join(subfolder, second_subfolder))

    export_file = os.path.join(destination_folder, 'crd.txt')
    try:
        with open(export_file, 'w') as ef:
            for foldername in copied_subfolders:
                ef.write(foldername + '\n')
        logging.info(f"Exported copied subfolders list to {export_file}")
    except Exception as e:
        logging.error(f"Failed to write export file {export_file}: {e}")

    # Export full list to crd_dtl.txt
    export_dtl_file = os.path.join(destination_folder, 'crd_dtl.txt')
    try:
        with open(export_dtl_file, 'w') as ef:
            for full_path in copied_full_paths:
                if os.path.isdir(full_path):
                    for root, _, files in os.walk(full_path):
                        for file in files:
                            file_path = os.path.join(root, file)
                            ef.write(file_path + '\n')
                else:
                    ef.write(full_path + '\n')
        logging.info(f"Exported full copied paths list to {export_dtl_file}")
    except Exception as e:
        logging.error(f"Failed to write export detail file {export_dtl_file}: {e}")

    env_vars = read_env_variables()
    nas_path = env_vars.get('NAS_PATH')
    nas_user = env_vars.get('NAS_USER')
    nas_pass = env_vars.get('NAS_PASS')

    if not nas_path or not nas_user or not nas_pass:
        logging.error("NAS_PATH, NAS_USER, or NAS_PASS environment variables are missing.")
        return

    batch_dir = os.path.join(destination_folder, 'batch_files')
    os.makedirs(batch_dir, exist_ok=True)
    batch_file = os.path.join(batch_dir, f'CRD_01_copy_{dist_period}.bat')
    with open(batch_file, 'w') as f:
        f.write(f'net use N: \\\\{nas_path}\\NAS {nas_pass} /user:{nas_user}\n')
        f.write(f'if not exist N:\\Societies\\{dist_period} mkdir N:\\Societies\\{dist_period}\n')
        f.write(f'xcopy /s /e /y "{destination_folder}\\*" "N:\\Societies\\{dist_period}\\"\n')
        f.write('net use N: /delete\n')
    logging.info(f"Created NAS batch: {batch_file}")

# ===== CRD 02 PIPELINE (simplified) =====

def crd_02_pipeline(dist_period, soc_dir):
    export_dtl_file = os.path.join("C:\\DIVA\\SOC", soc_dir, 'crd_dtl.txt')
    batch_dir = os.path.join("C:\\DIVA\\SOC", soc_dir, 'batch_files')
    os.makedirs(batch_dir, exist_ok=True)
    batch_file = os.path.join(batch_dir, f'CRD_02_copy_{dist_period}.sh')

    if not os.path.exists(export_dtl_file):
        logging.error(f"Export detail file does not exist: {export_dtl_file}")
        return

    try:
        with open(export_dtl_file, 'r') as ef, open(batch_file, 'w') as bf:
            created_dirs = set()
            written_copies = set()
            for line in ef:
                line = line.strip()
                parts = line.split('\\')
                if len(parts) > 5:
                    society_code_path = parts[5]
                    society_code_parts = society_code_path.split('_')
                    if len(society_code_parts) > 2:
                        part_0 = '_'.join(society_code_parts[:2])
                        part_2 = society_code_parts[2]
                        src_path = f"//volume1/NAS/Societies/{dist_period}/{society_code_path}/*"
                        dst_path = f"//volume1/{part_0}/downloads/{soc_dir}/CRD/{part_2}/"
                        if dst_path not in created_dirs:
                            bf.write(f'mkdir -p "{dst_path}"\n')
                            created_dirs.add(dst_path)
                        copy_pair = (src_path, dst_path)
                        if copy_pair not in written_copies:
                            bf.write(f'cp "{src_path}" "{dst_path}"\n')
                            written_copies.add(copy_pair)
        logging.info(f"Created CRD batch script: {batch_file}")
    except Exception as e:
        logging.error(f"Failed to create CRD batch script in crd_02_pipeline: {e}")


# ===== MAIN =====
def main():
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
    dist_period = input("Enter distribution period (202506 - CRD or ROY202506S - Payment): ").strip()
    soc_dir = input("Enter SOC directory name (e.g., Jun_2025): ").strip()
    distribution_type = input("Enter distribution type (CRD / PAYMENT): ").strip().upper()

    if not validate_dist_period(dist_period, distribution_type):
        sys.exit(1)
    
    if distribution_type == 'PAYMENT':
        payment_pipeline(dist_period, soc_dir)
        payment_02_pipeline(dist_period, soc_dir)
    elif distribution_type == 'CRD':
        crd_pipeline(dist_period, soc_dir)
        crd_02_pipeline(dist_period, soc_dir)
    else:
        logging.error("Invalid distribution type. Use CRD or PAYMENT.")
        sys.exit(1)

    logging.info("Process completed.")


if __name__ == '__main__':
    main()
