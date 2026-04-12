#!/usr/bin/env python3
import os
import json
import re
from pathlib import Path

# Directories to scan (add more if needed)
SEARCH_PATHS = [
    "/storage/0000-0000/Koreruss beats",
    "/storage/0000-0000/Android/data/com.termux/files/korerusscatalog/Koreruss beats",
    "/storage/0000-0000/Music",
    "/storage/0000-0000/Photos/Videos",
    "/storage/0000-0000/Koreruss beats/play liston beats",
    "/storage/0000-0000/Android/data/com.termux/files/koreruss-music-original",
    "/storage/0000-0000/Android/data/com.termux/files/koreruss-music-v2"
]

# Supported audio extensions
AUDIO_EXTS = {'.mp3', '.wav', '.flac', '.m4a', '.ogg', '.aac', '.wma'}

songs = []
for base in SEARCH_PATHS:
    if not os.path.exists(base):
        continue
    for root, dirs, files in os.walk(base):
        for file in files:
            ext = os.path.splitext(file)[1].lower()
            if ext in AUDIO_EXTS:
                # Create a relative path for the web (assuming files are served from a music server)
                full_path = os.path.join(root, file)
                # You might want to replace the local path with a URL prefix
                # For example, if your music server serves files at http://yourserver/stream/<path>
                # We'll just store the relative path; the frontend will prepend the server URL.
                songs.append({
                    "name": file,
                    "path": full_path,
                    "size": os.path.getsize(full_path)
                })

# Sort alphabetically
songs.sort(key=lambda x: x['name'].lower())

# Write to songs.json
with open('songs.json', 'w') as f:
    json.dump(songs, f, indent=2)

print(f"Found {len(songs)} songs. Saved to songs.json")
