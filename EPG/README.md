# Astro EPG Fetcher

This script (`epg.py`) retrieves Electronic Program Guide (EPG) data for various Astro channels from their respective URLs and exports the results into structured CSV files. It also logs the process for auditing and error tracking.

---

## 📂 Directory Structure

```
project_root/
├── epg.py                    # Main script
├── channel.csv               # Input CSV containing channels and URLs
├── astro_channel_reports/    # Output CSVs saved per channel
├── log/                      # Daily log files
```

---

## 🧾 Input File: `channel.csv`

The CSV must contain the following headers (case-insensitive):
- `channel` — the name of the channel
- `link` — the URL to fetch EPG data

**Example:**
```
channel,link
Astro AEC,http://epg.astro.com.my/...
Astro Ria,http://epg.astro.com.my/...
```

> Uses `utf-8-sig` encoding to handle BOM (important if editing in Excel).

---

## 🚀 What the Script Does

1. Reads the list of Astro channels and their URLs from `channel.csv`.
2. Fetches JSON data from each URL.
3. Parses the schedule (`response.schedule`) and extracts:
   - `eventId`, `title`, `description`, `datetime`, `eventStartMyt`, `eventEndMyt`, `duration`, `genre`, `subGenre`
4. Saves data to a CSV named like: `Astro_Ria_20250515.csv`
5. Logs all steps, errors, and results into a dated log file inside the `log/` directory.

---

## 🛠️ Error Handling

- Skips entries with missing or malformed data.
- Logs warnings or errors but continues processing remaining channels.
- Sanitizes filenames by replacing unsafe characters with `_`.

---

## 📋 CSV Output

Each CSV includes the following columns:

- `eventId`
- `title`
- `description`
- `datetime`
- `eventStartMyt`
- `eventEndMyt`
- `duration`
- `genre`
- `subGenre`

---

## 🗃️ Logs

Logs are saved in `log/DD_MM_YYYY.log` with details such as:
- Fetched URLs
- Number of events processed
- Warnings and errors encountered

---

## ✅ Requirements

- Python 3.8+
- Packages:
  - `requests`
  - `csv`
  - `datetime`
  - `logging`

Install using:
```bash
pip install requests
```

---

© MACP Workspace
