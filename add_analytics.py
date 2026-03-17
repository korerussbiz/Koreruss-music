#!/usr/bin/env python3
"""
Add Vercel Web Analytics script to all HTML files.
Also optionally add click tracking on download buttons.
"""
import os
import re
from pathlib import Path

# Replace with your actual Vercel Analytics site ID
SITE_ID = "prj_j9c0sAatnNFxidUcBoXUByMfokCt"  # <-- EDIT THIS

ANALYTICS_SCRIPT = f'''
<!-- Vercel Web Analytics -->
<script defer src="https://va.vercel-scripts.com/v1/analytics.js" data-site-id="{SITE_ID}"></script>
'''

# Also add an onClick event to download button for tracking (optional)
DOWNLOAD_BUTTON_TRACKING = '''
// Track download clicks
document.querySelectorAll('.download-btn').forEach(btn => {
    btn.addEventListener('click', () => {
        if (typeof window.va === 'function') {
            window.va('event', { name: 'download', data: { file: 'KorerussBizMiner_Setup.exe' } });
        }
    });
});
'''

def add_analytics_to_file(filepath):
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()

    # Check if analytics already present
    if 'va.vercel-scripts.com' in content:
        print(f"✓ Analytics already in {filepath.name}, skipping.")
        return

    # Insert before </body>
    if '</body>' not in content:
        print(f"⚠️ No </body> tag in {filepath.name}, skipping.")
        return

    new_content = content.replace('</body>', ANALYTICS_SCRIPT + '\n</body>')

    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(new_content)

    print(f"✅ Added analytics to {filepath.name}")

def add_tracking_script_to_download_page():
    download_page = Path('download.html')
    if not download_page.exists():
        print("⚠️ download.html not found, skipping download tracking.")
        return

    with open(download_page, 'r', encoding='utf-8') as f:
        content = f.read()

    # Insert tracking script before </body>
    if '</body>' not in content:
        return

    tracking_script = f'<script>{DOWNLOAD_BUTTON_TRACKING}</script>'
    if tracking_script in content:
        return

    new_content = content.replace('</body>', tracking_script + '\n</body>')
    with open(download_page, 'w', encoding='utf-8') as f:
        f.write(new_content)

    print("✅ Added download click tracking to download.html")

def main():
    if SITE_ID == "YOUR_SITE_ID_HERE":
        print("❌ Please edit add_analytics.py and set your SITE_ID first.")
        return

    # Process all HTML files
    html_files = Path('.').glob('*.html')
    for file in html_files:
        add_analytics_to_file(file)

    # Add click tracking on download page
    add_tracking_script_to_download_page()

if __name__ == '__main__':
    main()
