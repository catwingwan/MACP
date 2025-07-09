# SOC SFTP Sync v3

![Python](https://img.shields.io/badge/python-3.8%2B-blue)
![Status](https://img.shields.io/badge/status-stable-green)
![License](https://img.shields.io/badge/license-private-lightgrey)

A **unified automated Python pipeline** for **MACP SOC Distribution Processing**, handling **CRD** and **PAYMENT** file syncing, NAS batch generation, and detailed export tracking for audit and operational consistency.

---

## 🚀 Features

✅ Automated **copy from source to local ** for SOC distributions.  
✅ **Generates NAS sync batch scripts (.bat, .sh)** automatically.  
✅ Exports **`payment.txt`, `crd.txt`, `crd_dtl.txt`** for audit and Slack notifications if needed.  
✅ Handles **nested CRD structures** and **flat PAYMENT structures** cleanly.  
✅ **Clear logging** for easy monitoring and troubleshooting.

---

## 🛠️ Requirements

- **Python 3.8+**
- A `.env` file in the working directory with:
  ```
  NAS_PATH=your_nas_path
  NAS_USER=your_nas_user
  NAS_PASS=your_nas_password
  ```
- Network access to:
  - `source_location:\CRD\`
  - `source_location:\Dist_Payment_No\`
  - `destination_location:\SOC\`

---

## ⚙️ Usage

1️⃣ Clone or download this repository.  
2️⃣ Place `soc_sftp_sync_v3.py` in your working folder.  
3️⃣ Ensure your `.env` file is correctly configured.  
4️⃣ Open your terminal or command prompt:

```bash
python soc_sftp_sync_v3.py
```

5️⃣ Follow the prompts:
- Enter **Distribution Period**:
  - For `PAYMENT`: e.g., `202506S` (must end with `S`).
  - For `CRD`: e.g., `202506` (must **not** end with `S`).
- Enter **SOC Directory Name**: e.g., `Jun_2025`
- Enter **Distribution Type**: `CRD` or `PAYMENT` (case-insensitive).

---

## 📦 Outputs

### For PAYMENT
- Files copied to:
  ```
  destination_location:\SOC\\{soc_dir}\PAYMENT\
  ```
- Generates:
  - `payment.txt` (list of copied files)
  - `PAYMENT_copy_{dist_period}_01.bat` (NAS upload script)
  - `PAYMENT_copy_{dist_period}_02.sh` (NAS organization script)

### For CRD
- Files copied to:
  ```
  destination_location:\SOC\\{soc_dir}\
  ```
- Generates:
  - `crd.txt` (list of copied subfolders)
  - `crd_dtl.txt` (list of all copied files with paths)
  - `CRD_01_copy_{dist_period}.bat` (NAS upload script)
  - `CRD_02_copy_{dist_period}.sh` (NAS organization script)

---

## 🩺 Logging & Troubleshooting

- Logs are printed in the terminal for:
  - Missing folders or permissions
  - Missing `.env` credentials
  - Copy issues
- If the script exits with an error:
  - Verify `dist_period` format.
  - Check `.env` credentials.
  - Confirm network drive mappings.

---

## 📜 License

Private repository - for internal MACP operational use only.

---

