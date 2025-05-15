import os
import pandas as pd
from dotenv import load_dotenv

# --- Load environment variables ---
load_dotenv()

# Explicitly set PATH to include Oracle Instant Client directory before importing oracledb
os.environ["PATH"] = r".\app\Oracle\instantclient_19_26;" + os.environ.get("PATH", "")

import oracledb

# Enable thick mode for oracledb to support password verifier type 0x939
oracledb.init_oracle_client(lib_dir=r".\\app\\Oracle\\instantclient_19_26")

# Set TNS_ADMIN environment variable to the directory containing tnsnames.ora
os.environ["TNS_ADMIN"] = r".\\app\\Oracle\\network\\admin"

user = os.getenv("ORACLE_USER")
password = os.getenv("ORACLE_PASSWORD")

# Use TNS alias as DSN
dsn = os.getenv("ORACLE_TNS_ALIAS")
if not dsn:
    raise ValueError("ORACLE_TNS_ALIAS must be set in .env to use tnsnames.ora")


# --- Load IP_BASE.csv ---
ip_base_df = pd.read_csv("ISRC/IP_BASE.csv")
ip_base_list = ip_base_df[['IP_BASE_NO', 'NAME']].dropna(subset=['IP_BASE_NO', 'NAME'])

# --- SQL Template ---
sql_template = """
SELECT 
    worknum, 
    worknum_society, 
    e_title, 
    c_title, 
    performer AS artist_name, 
    NULL AS isrc
FROM (
    SELECT 
        m.worknum, m.worknum_society, m.genre_detail, 
        m.sub_title_id, m.e_title, m.c_title, 
        m.perform_language, m.performer
    FROM webupl_macp_title m
    UNION ALL
    SELECT 
        o.worknum, o.worknum_society, o.genre_detail, 
        o.sub_title_id, o.e_title, o.c_title, 
        o.perform_language, o.performer
    FROM webupl_other_title o
) a
WHERE 
    a.sub_title_id = 0
    AND NOT EXISTS (
        SELECT 1 FROM webupl_work_isrc i
        WHERE a.worknum = i.worknum_society
        AND a.worknum_society = i.worknum_society
    )
    AND EXISTS (
        SELECT 1 FROM webupl_work_ip_share s
        WHERE s.worknum = a.worknum
        AND s.worknum_society = a.worknum_society
        AND s.ip_society_code = '104'
        AND s.ip_base_no = :ip_base_no
    )
"""

# --- Export Directory ---
output_dir = "./ISRC/exported/"
os.makedirs(output_dir, exist_ok=True)

# --- Connect to Oracle DB ---
with oracledb.connect(user=user, password=password, dsn=dsn) as conn:
    for _, row in ip_base_list.iterrows():
        ip_base_no = row['IP_BASE_NO']
        name = row['NAME']
        print(f"Processing IP_BASE_NO: {ip_base_no}, NAME: {name}")
        try:
            result = pd.read_sql(sql_template, conn, params={"ip_base_no": ip_base_no})
        except UnicodeDecodeError as e:
            print(f"UnicodeDecodeError for IP_BASE_NO {ip_base_no}: {e}")
            continue
        output_path = f"{output_dir}ISRC_{name}.csv"
        result.to_csv(output_path, index=False)
        print(f"Exported to {output_path}")
