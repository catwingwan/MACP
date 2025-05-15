# Oracle DB to CSV Exporter

This script (`local_DB.py`) automates the process of extracting data from an Oracle database and saving it into a tab-delimited CSV file. It also supports copying the output to a network-shared folder for integration with downstream systems.

---

## 🚀 Features

- 🔒 Secure credential and path handling via `.env` file
- 📄 Reads SQL query from an external `.sql` file
- 🗃️ Exports query results as tab-delimited CSV with quoted fields
- 📤 Automatically copies output file to a destination directory
- 🛠️ Built-in Oracle Instant Client support (thick mode)

---

## 📁 Directory Structure

```
project_root/
├── local_DB.py
├── .env                         # Environment variables
├── queries/
│   └── your_query.sql           # SQL file referenced in .env
├── csvDB/                       # Output directory for generated CSV
└── network_folder/              # Target location for final CSV copy (set via .env)
```

---

## 🧾 .env Configuration

```env
ORACLE_INSTANTCLIENT_PATH=C:/path/to/instantclient_19_8
ORACLE_TNS_ADMIN=C:/path/to/network/admin
ORACLE_USER=your_db_user
ORACLE_PASSWORD=your_db_password
ORACLE_TNS_ALIAS=your_tns_alias
SQL_FILE_PATH=queries/your_query.sql
DESTINATION_FOLDER=network_folder/
```

Make sure the paths use **forward slashes** or are raw strings if using backslashes.

---

## 🛠️ Requirements

- Python 3.8+
- Oracle Instant Client (Thick mode required)
- Required Python packages:
  - `pandas`
  - `python-dotenv`
  - `oracledb`

Install them via pip:
```bash
pip install pandas python-dotenv oracledb
```

---

## 📦 Output Format

The output CSV:
- Is saved in `csvDB/`
- Is named like: `LocalDB_YYYYMMDD.csv`
- Uses **tab delimiters**
- Encloses all fields in double quotes for safety

---

## 🧪 How It Works

1. Loads Oracle DB and path settings from `.env`
2. Reads and executes SQL from the specified `.sql` file
3. Saves the results as a CSV in `csvDB/`
4. Copies the CSV to `DESTINATION_FOLDER`

---

## 📋 Logs & Feedback

- Success and error messages are printed to the console
- Basic exception handling is included for missing paths or connection issues

---

© MACP Workspace
