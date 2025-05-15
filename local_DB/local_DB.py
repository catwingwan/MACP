import os
import pandas as pd
from dotenv import load_dotenv
from datetime import datetime
import csv
import shutil

# --- Load environment variables ---
load_dotenv()

# Load Oracle Instant Client path from env
instant_client_path = os.getenv("ORACLE_INSTANTCLIENT_PATH")
if not instant_client_path:
    raise ValueError("ORACLE_INSTANTCLIENT_PATH must be set in .env")

# Explicitly set PATH to include Oracle Instant Client directory before importing oracledb
os.environ["PATH"] = instant_client_path + ";" + os.environ.get("PATH", "")

import oracledb

# Enable thick mode for oracledb to support password verifier type 0x939
oracledb.init_oracle_client(lib_dir=instant_client_path)

# Load TNS_ADMIN path from env
tns_admin_path = os.getenv("ORACLE_TNS_ADMIN")
if not tns_admin_path:
    raise ValueError("ORACLE_TNS_ADMIN must be set in .env")
os.environ["TNS_ADMIN"] = tns_admin_path

user = os.getenv("ORACLE_USER")
password = os.getenv("ORACLE_PASSWORD")

# Use TNS alias as DSN
dsn = os.getenv("ORACLE_TNS_ALIAS")
if not dsn:
    raise ValueError("ORACLE_TNS_ALIAS must be set in .env")

# Load SQL file path from env
sql_file_path = os.getenv("SQL_FILE_PATH")
if not sql_file_path:
    raise ValueError("SQL_FILE_PATH must be set in .env")

# Resolve full path of SQL file relative to current file directory
sql_file_path = os.path.join(os.path.dirname(__file__), sql_file_path)

# --- Read SQL query from file ---
with open(sql_file_path, "r", encoding="utf-8") as f:
    sql_query = f.read().strip().rstrip(';')

# --- Export Directory ---
output_dir = os.path.join(os.path.dirname(__file__), "csvDB")
os.makedirs(output_dir, exist_ok=True)

# --- Connect to Oracle DB and execute query ---
with oracledb.connect(user=user, password=password, dsn=dsn) as conn:
    with conn.cursor() as cursor:
        cursor.execute(sql_query)
        columns = [col[0] for col in cursor.description]
        rows = cursor.fetchall()

# --- Load results into DataFrame ---
df = pd.DataFrame(rows, columns=columns)

# --- Export to CSV with tab separator and quoted fields ---
today_str = datetime.now().strftime("%Y%m%d")
output_path = os.path.join(output_dir, f"LocalDB_{today_str}.csv")
df.to_csv(output_path, sep='\t', index=False, quoting=csv.QUOTE_ALL)
print(f"Exported query results to {output_path}")

# --- Copy exported CSV to network destination folder ---
destination_folder = os.getenv("DESTINATION_FOLDER")
if not destination_folder:
    raise ValueError("DESTINATION_FOLDER must be set in .env")

try:
    shutil.copy(output_path, destination_folder)
    print(f"Successfully copied {output_path} to {destination_folder}")
except Exception as e:
    print(f"Error copying file to network path: {e}")
