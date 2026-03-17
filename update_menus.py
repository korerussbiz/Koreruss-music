#!/usr/bin/env python3
"""
Automatically add "Download Miner" link to all HTML navigation menus.
Skips download.html to avoid self-linking.
"""
import os
import re
from pathlib import Path

def add_link_to_html(filepath):
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()

    # If the link already exists, skip
    if 'href="download.html"' in content:
        print(f"✓ Link already present in {filepath.name}, skipping.")
        return

    # Pattern to find navigation div with links
    # This assumes a structure like <div class="nav"> ... </div>
    # We'll insert the new link before the closing </div>
    pattern = r'(<div\s+class="nav">.*?)(</div>)'
    match = re.search(pattern, content, re.DOTALL)
    if not match:
        print(f"⚠️ Could not find navigation div in {filepath.name}, skipping.")
        return

    nav_content = match.group(1)
    closing_div = match.group(2)

    # Insert the new link after the last existing link (preserve indentation)
    # Find the last link in nav_content and insert after it
    link_pattern = r'<a\s+href="[^"]+"[^>]*>[^<]*</a>'
    links = list(re.finditer(link_pattern, nav_content))
    if links:
        last_link = links[-1]
        insert_pos = last_link.end()
        # Insert the new link with proper spacing
        new_nav = nav_content[:insert_pos] + '\n            ' + '<a href="download.html">Download Miner</a>' + nav_content[insert_pos:]
    else:
        # No links? Insert right after the opening div
        div_end = nav_content.find('>') + 1
        new_nav = nav_content[:div_end] + '\n            ' + '<a href="download.html">Download Miner</a>' + nav_content[div_end:]

    new_content = content.replace(nav_content + closing_div, new_nav + closing_div)

    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(new_content)

    print(f"✅ Added link to {filepath.name}")

def main():
    html_files = Path('.').glob('*.html')
    for file in html_files:
        if file.name == 'download.html':
            continue
        add_link_to_html(file)

if __name__ == '__main__':
    main()
