import requests
import pandas as pd
from requests.auth import HTTPBasicAuth
import time
from urllib.parse import quote

import base64
import os

# Spotify API credentials - you need to set these environment variables or replace with your client id and secret
SPOTIFY_CLIENT_ID = os.getenv('SPOTIFY_CLIENT_ID', '')
SPOTIFY_CLIENT_SECRET = os.getenv('SPOTIFY_CLIENT_SECRET', '')

# Alternatively, you can directly assign your token here if you have a valid token
SPOTIFY_STATIC_TOKEN = ''

import threading
import time

_token_lock = threading.Lock()
_token_cache = {
    'token': None,
    'expires_at': 0
}

def get_spotify_token():
    """
    Obtain and cache Spotify API token using Client Credentials Flow.
    Automatically refreshes token when expired.
    """
    import requests
    import time

    with _token_lock:
        current_time = time.time()
        if _token_cache['token'] and _token_cache['expires_at'] > current_time + 60:
            # Return cached token if valid for at least 60 more seconds
            return _token_cache['token']

        auth_url = 'https://accounts.spotify.com/api/token'
        auth_header = base64.b64encode(f"{SPOTIFY_CLIENT_ID}:{SPOTIFY_CLIENT_SECRET}".encode()).decode()
        headers = {
            'Authorization': f'Basic {auth_header}',
            'Content-Type': 'application/x-www-form-urlencoded'
        }
        data = {'grant_type': 'client_credentials'}

        try:
            response = requests.post(auth_url, headers=headers, data=data)
            response.raise_for_status()
            json_resp = response.json()
            token = json_resp.get('access_token')
            expires_in = json_resp.get('expires_in', 3600)  # default 1 hour
            if not token:
                raise Exception('Failed to obtain access token')
            _token_cache['token'] = token
            _token_cache['expires_at'] = current_time + expires_in
            return token
        except requests.exceptions.RequestException as e:
            print(f"Error obtaining Spotify token: {str(e)}")
            return None

def get_isrc(song_title, artist):
    if pd.isna(song_title) or pd.isna(artist) or not str(song_title).strip() or not str(artist).strip():
        return 'Missing Data'
        
    # Use English title if available, otherwise use Chinese title
    search_title = str(song_title).strip() if not pd.isna(song_title) else str(artist).strip()
    search_artist = str(artist).strip()
    
    query = f"track:{search_title} artist:{search_artist}"
    url = f"https://api.spotify.com/v1/search?q={quote(query)}&type=track&limit=1"
    
    token = get_spotify_token()
    if not token:
        print("Failed to obtain Spotify token.")
        return 'API Error'
    
    headers = {'Authorization': f'Bearer {token}'}
    
    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        
        tracks = response.json().get('tracks', {}).get('items', [])
        
        if tracks:
            return tracks[0].get('external_ids', {}).get('isrc', 'No ISRC Found')
        return 'Track Not Found'
    except requests.exceptions.RequestException as e:
        print(f"Error searching for {search_title} by {search_artist}: {str(e)}")
        return 'API Error'

def process_song_table(input_file, output_file):
    # Read input file with error handling for malformed lines
    if input_file.endswith('.csv'):
        df = pd.read_csv(input_file, sep=',', on_bad_lines='warn')
    else:
        df = pd.read_excel(input_file)
    
    # Print debug info: actual columns read
    print(f"DEBUG: Columns in input file: {list(df.columns)}")
    
    # Normalize columns to lowercase for case-insensitive matching
    df.columns = [col.lower() for col in df.columns]
    
    # Check for required columns
    required_columns = {'e_title', 'c_title', 'artist_name'}
    missing_columns = required_columns - set(df.columns)
    if missing_columns:
        raise ValueError(f"Input file is missing required columns: {missing_columns}")
    
    # Add ISRC column by searching each track, skipping rows with missing data
    results = []
    for idx, row in df.iterrows():
        # Skip rows missing required data
        if pd.isna(row['e_title']) and pd.isna(row['c_title']):
            results.append('Missing Title')
            continue
        if pd.isna(row['artist_name']):
            results.append('Missing Artist')
            continue
        
        # Try English title first, fall back to Chinese title if needed
        title_to_search = row['e_title'] if not pd.isna(row['e_title']) else row['c_title']
        
        isrc = get_isrc(title_to_search, row['artist_name'])
        results.append(isrc)
        
        # Add delay to avoid rate limiting (Spotify allows ~30 requests per second)
        time.sleep(0.1)  # 100ms delay between requests
        
        # Print progress
        if (idx + 1) % 10 == 0:
            print(f"Processed {idx + 1}/{len(df)} tracks")
    
    df['isrc'] = results
    
    # Save results
    if output_file.endswith('.csv'):
        df.to_csv(output_file, index=False, sep='\t')
    else:
        df.to_excel(output_file, index=False)

# Example usage
input_filename = r'.\ISRC\xisrc.csv'  # or .xlsx
output_filename = r'.\ISRC\output_visrc.csv'  # or .xlsx
process_song_table(input_filename, output_filename)
