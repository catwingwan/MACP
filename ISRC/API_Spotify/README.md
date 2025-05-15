# ISRC Public Export Script

This script extracts work entries from an Oracle database for IP bases that have not yet been associated with an ISRC, and exports them to individual CSV files.

## 📂 Directory Structure

```
project_root/
├── ISRC/
│   ├── IP_BASE.csv          # Input: IP base numbers and names
│   └── exported/            # Output: Individual CSVs per IP base
├── app/
│   └── Oracle/
│       ├── instantclient_19_26/  # Oracle client library
│       └── network/
│           └── admin/
│               └── tnsnames.ora  # TNS configuration
├── ISRC_Pub.py              # Main script
├── .env                     # Environment variables
```

## 🔧 Requirements

- Python 3.8+
- Oracle Instant Client (thick mode required)
- Packages:
  - `pandas`
  - `python-dotenv`
  - `oracledb`

Install required packages:
```bash
pip install pandas python-dotenv oracledb
```

## 🧪 Environment Setup

Create a `.env` file in the project root with the following content:

```env
ORACLE_USER=your_db_user
ORACLE_PASSWORD=your_db_password
ORACLE_TNS_ALIAS=your_tns_alias
```

Ensure the `tnsnames.ora` file contains the alias specified in `ORACLE_TNS_ALIAS`.

## 🚀 Running the Script

From the root directory:
```bash
python ISRC_Pub.py
```

Each valid IP base entry from `IP_BASE.csv` will trigger a SQL query and output a CSV to `./ISRC/exported/`.

## 🛠️ Notes

- The script uses **Oracle thick mode** to support specific password verifier requirements.
- Only records **not already associated with an ISRC** are exported.
- SQL targets works from `webupl_macp_title` and `webupl_other_title`.

## 📞 Troubleshooting

- Ensure Oracle Instant Client is correctly installed and its path is configured.
- If a `UnicodeDecodeError` occurs, the error is caught and logged; that IP base is skipped.
- Ensure the `.env` file is correctly set and the Oracle TNS alias is defined in `tnsnames.ora`.

---

© MACP Workspace
