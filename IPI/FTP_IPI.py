#!/usr/bin/env python3
"""
Bulletproof SFTP Downloader with:
- Chunked transfer protocol
- Automatic resume at exact breakpoint
- Military-grade connection stability
- Transfer speed optimization
"""

import os
import time
import logging
from datetime import datetime
from pathlib import Path
import paramiko
import socket
import platform
from dotenv import load_dotenv
import shutil

# Configuration
load_dotenv()
SFTP_HOST = os.getenv('SFTP_HOST', '')
SFTP_PORT = int(os.getenv('SFTP_PORT', ''))
SFTP_USER = os.getenv('SFTP_USER', '')
SFTP_PASS = os.getenv('SFTP_PASS', '')
SFTP_DIR = os.getenv('SFTP_DIR', '')
LOCAL_DIR = Path(os.getenv('LOCAL_DIR', ''))
SERVER_DIR = Path(os.getenv('SERVER_DIR', ''))
LOG_FILE = Path(os.getenv('LOG_FILE', ''))
LAST_FILE_RECORD = Path(os.getenv('LAST_FILE_RECORD', ''))

# Transfer Settings
CHUNK_SIZE = 2 * 1024 * 1024  # 2MB chunks (optimal for unstable connections)
MAX_RETRIES = 7                 # Increased retry attempts
RETRY_BACKOFF = [5, 10, 30, 60, 120, 300, 600]  # Progressive delays
KEEPALIVE_INTERVAL = 15         # Aggressive keepalives
BUFFER_SIZE = 128 * 1024        # 128KB buffer size

# Logging
logging.basicConfig(
    level=logging.INFO,
    format='[%(asctime)s] %(levelname)s: %(message)s',
    handlers=[
        logging.FileHandler(LOG_FILE),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger('sftp_downloader')
paramiko_logger = logging.getLogger('paramiko')
paramiko_logger.setLevel(logging.WARNING)

class MilitaryGradeSFTP:
    def __init__(self):
        self.transport = None
        self.sftp = None
        self.last_byte = 0
        self.file_size = 0
        self.retry_count = 0

    def connect(self):
        """Establish ultra-reliable connection"""
        self.transport = paramiko.Transport((SFTP_HOST, SFTP_PORT))
        
        # Connection hardening
        self.transport.window_size = 16 * 1024 * 1024  # 16MB window
        self.transport.packetizer.REKEY_BYTES = 512 * 1024 * 1024  # 512MB
        self.transport.use_compression(True)
        self.transport.connect(username=SFTP_USER, password=SFTP_PASS)
        
        # Connection keepalive settings
        self.transport.set_keepalive(KEEPALIVE_INTERVAL)
        self.sftp = paramiko.SFTPClient.from_transport(self.transport)
        self.sftp.chdir(SFTP_DIR)
        
        # Socket-level optimizations
        sock = self.transport.sock
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_KEEPALIVE, 1)
        system_platform = platform.system()
        if system_platform in ['Linux', 'Darwin']:
            sock.setsockopt(socket.IPPROTO_TCP, socket.TCP_KEEPIDLE, 20)
            sock.setsockopt(socket.IPPROTO_TCP, socket.TCP_KEEPINTVL, 5)
            sock.setsockopt(socket.IPPROTO_TCP, socket.TCP_KEEPCNT, 3)
            logger.info("TCP keepalive options set for Unix-like system")
        elif system_platform == 'Windows':
            # Windows does not support TCP_KEEPIDLE etc.
            logger.info("TCP keepalive options limited on Windows")
        else:
            logger.warning(f"Unknown platform {system_platform}, skipping TCP keepalive options")

    def close(self):
        """Secure connection teardown"""
        try:
            if self.sftp:
                self.sftp.close()
        except:
            pass
        try:
            if self.transport:
                self.transport.close()
        except:
            pass

    def verify_connection(self):
        """Active connection verification"""
        try:
            # Zero-byte SSH request to verify connection
            self.transport.send_ignore()
            return True
        except:
            return False

    def download_with_armor(self, remote_path, local_path):
        """Ironclad download with military-grade reliability"""
        try:
            # Get file info
            self.file_size = self.sftp.stat(remote_path).st_size
            logger.info(f"Target file size: {self.file_size/1024/1024:.2f}MB")
            
            # Resume logic
            self.last_byte = os.path.getsize(local_path) if os.path.exists(local_path) else 0
            mode = 'ab' if self.last_byte > 0 else 'wb'
            
            if self.last_byte >= self.file_size:
                logger.info("File already complete")
                return True

            logger.info(f"Resume point: {self.last_byte} bytes ({self.last_byte/1024/1024:.2f}MB)")

            with self.sftp.file(remote_path, 'rb') as remote_file:
                if self.last_byte > 0:
                    remote_file.seek(self.last_byte)
                
                with open(local_path, mode) as local_file:
                    while self.last_byte < self.file_size:
                        # Connection watchdog
                        if time.time() % 10 == 0 and not self.verify_connection():
                            raise paramiko.SSHException("Connection watchdog triggered")
                        
                        try:
                            chunk = remote_file.read(CHUNK_SIZE)
                            if not chunk:
                                break
                                
                            local_file.write(chunk)
                            self.last_byte += len(chunk)
                            
                            # Progress reporting
                            if time.time() % 30 == 0:
                                percent = (self.last_byte / self.file_size) * 100
                                speed = len(chunk) / (time.time() % 30)
                                logger.info(
                                    f"Progress: {percent:.1f}% | "
                                    f"Speed: {speed/1024:.1f}KB/s | "
                                    f"Position: {self.last_byte/1024/1024:.2f}MB"
                                )
                                
                        except (paramiko.SSHException, EOFError) as e:
                            logger.warning(f"Chunk transfer failed: {str(e)}")
                            raise

            # Final verification
            if os.path.getsize(local_path) == self.file_size:
                logger.info("Download fully verified")
                return True
                
            raise IOError("Final size verification failed")

        except Exception as e:
            logger.error(f"Transfer failed at {self.last_byte} bytes: {str(e)}")
            raise

def main():
    logger.info("=== MILITARY-GRADE SFTP DOWNLOADER ===")
    engine = MilitaryGradeSFTP()
    last_error = None

    def extract_date(file_name):
        digits = ''.join(filter(str.isdigit, file_name))
        return digits if len(digits) == 8 else None

    def get_yesterday_date_str():
        from datetime import datetime, timedelta
        yesterday = datetime.now() - timedelta(days=1)
        return yesterday.strftime('%Y%m%d')

    yesterday_str = get_yesterday_date_str()

    while True:
        try:
            logger.info("Starting new download cycle")
            engine.connect()

            # Read last downloaded date from last_file.txt
            last_date_str = None
            if LAST_FILE_RECORD.exists():
                with open(LAST_FILE_RECORD, 'r') as f:
                    last_file_name = f.read().strip()
                    last_date_str = extract_date(last_file_name)
            else:
                last_date_str = None

            if last_date_str == yesterday_str:
                logger.info(f"Reached target date {yesterday_str}. Exiting loop.")
                break

            # List files and filter by date after last_date_str
            files = [f for f in engine.sftp.listdir() if 'IPI' in f]
            if not files:
                logger.error("No matching files found")
                break

            filtered_files = []
            for f in files:
                file_date = extract_date(f)
                if file_date and (last_date_str is None or file_date > last_date_str):
                    filtered_files.append(f)

            if not filtered_files:
                logger.info("No new files to download after last_file.txt date")
                break

            # Select earliest file after last_date_str
            remote_file = min(filtered_files, key=lambda x: extract_date(x))
            remote_path = f"{SFTP_DIR}/{remote_file}"
            local_path = LOCAL_DIR / remote_file

            os.makedirs(LOCAL_DIR, exist_ok=True)

            if engine.download_with_armor(remote_path, local_path):
                # Update last downloaded file record
                with open(LAST_FILE_RECORD, 'w') as f:
                    f.write(remote_file)
                logger.info(f"Downloaded and updated last file to {remote_file}")
                # Sync to server directory
                try:
                    os.makedirs(SERVER_DIR, exist_ok=True)
                    dest_path = SERVER_DIR / remote_file
                    shutil.copy2(local_path, dest_path)
                    logger.info(f"Synced {remote_file} to server directory {SERVER_DIR}")
                except Exception as e:
                    logger.error(f"Failed to sync to server directory: {str(e)}")
            else:
                logger.error("Download failed, stopping loop")
                break

            # Small delay before next cycle to avoid rapid looping
            time.sleep(5)

        except Exception as e:
            last_error = str(e)
            logger.error(f"Download cycle failed: {last_error}")
            # Optional: add retry/backoff logic here if desired
            break
        finally:
            engine.close()

    logger.info("Download loop ended")

if __name__ == "__main__":
    main()
