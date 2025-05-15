# Military-Grade SFTP IPI File Downloader

This script (`FTP_IPI.py`) provides a **resumable**, **robust**, and **automated** SFTP download solution tailored for large or mission-critical file transfers — especially `IPI` files. It ensures high resilience over unstable connections and logs every step of the process.

---

## 🚀 Features

- ✅ Resumes interrupted downloads from exact byte
- 📦 Chunked download (2MB) to balance performance and stability
- 🔐 TCP keepalive & SSH rekey settings for long sessions
- 🕒 Automatic retry/backoff logic (configurable)
- 📂 Filters files by date and downloads only the latest
- 📝 Logs all actions to file and console
- 🔄 Syncs downloaded file to a server directory
- 🧠 Remembers last successful download

---

## 📁 Directory Structure

```
project_root/
├── FTP_IPI.py
├── .env                      # Stores connection and directory config
├── last_file.txt             # Tracks last successful download
├── logs/                     # Contains runtime logs
├── LOCAL_DIR/                # Downloaded files are saved here
└── SERVER_DIR/               # Synced output directory
```

---

## 🧾 .env Configuration

Set the following variables in a `.env` file:

```env
SFTP_HOST=your.sftp.server
SFTP_PORT=22
SFTP_USER=your_username
SFTP_PASS=your_password
SFTP_DIR=/remote/path
LOCAL_DIR=./local_downloads
SERVER_DIR=./synced_server
LOG_FILE=./logs/sftp_transfer.log
LAST_FILE_RECORD=./last_file.txt
```

---

## 🛠️ Requirements

- Python 3.8+
- Packages:
  - `paramiko`
  - `python-dotenv`

Install dependencies:
```bash
pip install paramiko python-dotenv
```

---

## 🧪 How It Works

1. Connects to SFTP server using credentials from `.env`
2. Reads `last_file.txt` to identify the last file processed
3. Lists remote files matching pattern `"IPI*"`
4. Selects the **next file chronologically**
5. Resumes or starts download with 2MB chunks
6. Validates final file size
7. Syncs file to `SERVER_DIR`
8. Updates `last_file.txt`

---

## 📋 Logging

All events are logged to:
- `LOG_FILE` path specified in `.env`
- Console output (for real-time monitoring)

Logged events include:
- Connection attempts
- Progress updates
- Transfer speed
- Failures and retries
- Sync completion

---

## ⚠️ Error Handling

- Automatically retries connection failures and interruptions
- Logs partial failures for review
- Does not re-download already completed files

---

© MACP Workspace
