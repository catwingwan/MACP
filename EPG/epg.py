import requests
import csv
from datetime import datetime
import re
import os
import logging

# Function to sanitize filename by replacing or removing unsafe characters
def sanitize_filename(name):
    return re.sub(r'[^a-zA-Z0-9_-]', '_', name)

# Get current date in YYYYMMDD format
current_date = datetime.now().strftime("%Y%m%d")

# Directory to save reports
output_dir = "astro_channel_reports"
os.makedirs(output_dir, exist_ok=True)

# Directory to save logs
log_dir = "log"
os.makedirs(log_dir, exist_ok=True)

# Configure logging with date_month_year format in filename
log_filename = datetime.now().strftime("%d_%m_%Y") + ".log"
log_path = os.path.join(log_dir, log_filename)
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(log_path, encoding='utf-8'),
        logging.StreamHandler()
    ]
)

# Read channel names and URLs from channel.csv with utf-8-sig encoding to handle BOM
channels = []
with open('channel.csv', newline='', encoding='utf-8-sig') as csvfile:
    reader = csv.DictReader(csvfile)
    logging.info(f"CSV fieldnames: {reader.fieldnames}")
    for row in reader:
        # Normalize keys by stripping and lowercasing
        row_normalized = {k.strip().lower(): v.strip() for k, v in row.items() if k and v}
        channel_name = row_normalized.get('channel')
        link = row_normalized.get('link')
        if channel_name and link:
            channels.append((channel_name, link))

logging.info(f"Found {len(channels)} channels to process.")

# Iterate over each channel and fetch data, write separate CSV for each channel
for channel_name, single_url in channels:
    logging.info(f"Processing channel: {channel_name} URL: {single_url}")
    try:
        response = requests.get(single_url)
        if response.status_code != 200:
            logging.warning(f"Failed to fetch data for {channel_name} with status code {response.status_code}")
            continue
        if not response.content:
            logging.warning(f"Empty response content for {channel_name}")
            continue
        try:
            data = response.json()
        except Exception as e:
            logging.error(f"JSON decode error for {channel_name}: {e}")
            logging.error(f"Response content: {response.text[:200]}")  # print first 200 chars
            continue
    except Exception as e:
        logging.error(f"Exception occurred while fetching data for {channel_name}: {e}")
        continue

    # Prepare to extract relevant events for this channel
    programs = []

    # Navigate to the schedule inside the JSON
    schedule_data = data.get('response', {}).get('schedule', {})
    if not schedule_data:
        logging.warning(f"No schedule data found for {channel_name}")
        continue

    # Loop through each day's schedule
    for date, events in schedule_data.items():
        for event in events:
            if 'eventId' in event:
                programs.append({
                    'eventId': event.get('eventId'),
                    'title': event.get('title'),
                    'description': event.get('description'),
                    'datetime': event.get('datetime'),
                    'eventStartMyt': event.get('eventStartMyt'),
                    'eventEndMyt': event.get('eventEndMyt'),
                    'duration': event.get('duration'),
                    'genre': event.get('genre'),
                    'subGenre': event.get('subGenre'),
                })

    if not programs:
        logging.warning(f"No program events found for {channel_name}")
        continue

    # Sanitize channel name for filename
    safe_channel_name = sanitize_filename(channel_name)

    # Define output filename with channel name and date inside the output directory
    output_file = os.path.join(output_dir, f"{safe_channel_name}_{current_date}.csv")

    # Write to CSV
    try:
        with open(output_file, 'w', newline='', encoding='utf-8') as csvfile:
            fieldnames = ['eventId', 'title', 'description', 'datetime', 'eventStartMyt', 'eventEndMyt', 'duration', 'genre', 'subGenre']
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

            writer.writeheader()
            for program in programs:
                writer.writerow(program)
        logging.info(f"✅ Successfully written {len(programs)} records to {output_file}")
    except Exception as e:
        logging.error(f"Exception occurred while writing file for {channel_name}: {e}")
