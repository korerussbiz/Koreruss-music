#!/usr/bin/env python3
import json
import requests
import sys
from pathlib import Path

WALLET = "0xCf974b9e14766f839D8C59bDA1D4Dff3CF3f8b33"
CONTRACT = "0x72c997ED37F786829F01f6a73B14F6Bdd61c2B94"
OUTPUT = "public/nft-gallery.html"

# ------------------------------------------------------------------
# 1. Try to fetch NFTs using OpenSea API (public, no key)
# ------------------------------------------------------------------
def fetch_from_opensea():
    url = f"https://api.opensea.io/api/v2/chain/polygon/account/{WALLET}/nfts?limit=100"
    try:
        r = requests.get(url, timeout=15)
        if r.status_code != 200:
            print(f"OpenSea API returned {r.status_code}")
            return None
        data = r.json()
        nfts = []
        for nft in data.get("nfts", []):
            nfts.append({
                "name": nft.get("name") or f"Token #{nft.get('identifier')}",
                "image": nft.get("display_image_url") or nft.get("image_url") or "https://via.placeholder.com/250",
                "tokenId": nft.get("identifier"),
                "contract": nft.get("contract")
            })
        return nfts
    except Exception as e:
        print(f"OpenSea fetch error: {e}")
        return None

# ------------------------------------------------------------------
# 2. Fallback: manual list (you can edit this with your token IDs)
# ------------------------------------------------------------------
def fallback_manual():
    # If you know your token IDs, list them here. Example:
    token_ids = [
        "1", "2", "3", "4", "5", "6", "7", "8", "9", "10",
        "34", "35", "36", "37"
    ]
    nfts = []
    for tid in token_ids:
        # Construct a reasonable name and image placeholder
        name = f"Koreruss NFT #{tid}"
        # You can replace with actual image URLs if you know them
        image = f"https://via.placeholder.com/250?text=Token+{tid}"
        nfts.append({
            "name": name,
            "image": image,
            "tokenId": tid,
            "contract": CONTRACT
        })
    return nfts

# ------------------------------------------------------------------
# 3. Generate HTML
# ------------------------------------------------------------------
def generate_html(nfts):
    cards = []
    for nft in nfts:
        name = nft["name"][:50]
        img = nft["image"]
        tid = nft["tokenId"]
        contract = nft["contract"]
        opensea_url = f"https://opensea.io/assets/polygon/{contract}/{tid}"
        cards.append(f'''
        <div class="nft-card">
            <img src="{img}" alt="{name}" onerror="this.src='https://via.placeholder.com/250?text=Image+Error'">
            <h3>{name}</h3>
            <p>Token ID: {tid}</p>
            <a href="{opensea_url}" target="_blank">View on OpenSea</a>
        </div>
        ''')
    html = f'''<!DOCTYPE html>
<html>
<head>
    <title>Koreruss NFT Gallery</title>
    <meta charset="UTF-8">
    <style>
        body {{ font-family: Arial; margin: 20px; background: #f5f5f5; text-align: center; }}
        .gallery {{ display: flex; flex-wrap: wrap; justify-content: center; gap: 20px; margin-top: 20px; }}
        .nft-card {{ background: white; width: 250px; padding: 10px; border-radius: 10px; box-shadow: 0 2px 8px rgba(0,0,0,0.1); }}
        .nft-card img {{ width: 100%; border-radius: 8px; max-height: 250px; object-fit: contain; }}
        .nft-card h3 {{ font-size: 1em; margin: 10px 0; }}
        .nft-card a {{ display: inline-block; margin-top: 10px; padding: 5px 10px; background: #2081e2; color: white; text-decoration: none; border-radius: 5px; }}
        .ad {{ margin: 30px auto; max-width: 728px; background: #e0e0e0; padding: 15px; border-radius: 8px; }}
        .ad a {{ color: #2081e2; font-weight: bold; text-decoration: none; }}
    </style>
</head>
<body>
    <h1>Koreruss NFT Collection</h1>
    <div class="gallery">{''.join(cards)}</div>
    <div class="ad">
        🔥 <a href="/merch.html" target="_blank">Get your NFT printed on a T‑Shirt! Limited time offer.</a> 🔥
    </div>
</body>
</html>'''
    return html

# ------------------------------------------------------------------
# 4. Main
# ------------------------------------------------------------------
def main():
    print("Trying to fetch NFTs from OpenSea...")
    nfts = fetch_from_opensea()
    if not nfts:
        print("OpenSea failed. Using manual fallback list.")
        nfts = fallback_manual()
    else:
        print(f"Fetched {len(nfts)} NFTs from OpenSea.")
    html = generate_html(nfts)
    with open(OUTPUT, "w") as f:
        f.write(html)
    print(f"Gallery written to {OUTPUT}")

if __name__ == "__main__":
    main()
