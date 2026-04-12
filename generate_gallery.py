#!/usr/bin/env python3
import os
import json
import requests
import time
from pathlib import Path
from dotenv import load_dotenv

load_dotenv(Path.home() / "koreruss.env")

WALLET = "0xCf974b9e14766f839D8C59bDA1D4Dff3CF3f8b33"
CONTRACT = "0x72c997ED37F786829F01f6a73B14F6Bdd61c2B94"
OUTPUT = "public/nft-gallery.html"

def try_polygonscan():
    key = os.getenv("POLYGONSCAN_API_KEY") or os.getenv("ETHERSCAN_API_KEY")
    if not key: return None
    url = f"https://api.polygonscan.com/api?module=account&action=tokennfttx&address={WALLET}&sort=asc&apikey={key}"
    try:
        r = requests.get(url, timeout=10)
        data = r.json()
        if data.get("status") != "1": return None
        txs = data.get("result", [])
        token_map = {}
        for tx in txs:
            tid = tx.get("tokenID")
            if tid and tid not in token_map:
                token_map[tid] = tx.get("tokenURI")
        nfts = []
        for tid, uri in token_map.items():
            if uri:
                meta_url = uri.replace("ipfs://", "https://ipfs.io/ipfs/")
                try:
                    meta = requests.get(meta_url, timeout=10).json()
                except:
                    meta = {}
                name = meta.get("name", f"Token {tid}")
                image = meta.get("image", "")
                if image.startswith("ipfs://"):
                    image = image.replace("ipfs://", "https://ipfs.io/ipfs/")
                nfts.append({"name": name, "image": image, "tokenId": tid, "contract": CONTRACT})
        return nfts
    except:
        return None

def try_opensea():
    url = f"https://api.opensea.io/api/v2/chain/polygon/account/{WALLET}/nfts?limit=50"
    try:
        r = requests.get(url, timeout=10)
        if r.status_code != 200: return None
        data = r.json()
        nfts = []
        for nft in data.get("nfts", []):
            nfts.append({
                "name": nft.get("name", f"Token {nft.get('identifier')}"),
                "image": nft.get("display_image_url") or nft.get("image_url") or "",
                "tokenId": nft.get("identifier"),
                "contract": nft.get("contract")
            })
        return nfts
    except:
        return None

def try_covalent():
    key = os.getenv("COVALENT_API_KEY")
    if not key: return None
    url = f"https://api.covalenthq.com/v1/137/address/{WALLET}/balances_v2/?nft=true&key={key}"
    try:
        r = requests.get(url, timeout=10)
        if r.status_code != 200: return None
        data = r.json()
        items = data.get("data", {}).get("items", [])
        nfts = []
        for item in items:
            if item.get("type") == "nft":
                nft_data = item.get("nft_data", [{}])[0]
                ext_data = nft_data.get("external_data", {})
                image = ext_data.get("image", "")
                if image.startswith("ipfs://"):
                    image = image.replace("ipfs://", "https://ipfs.io/ipfs/")
                nfts.append({
                    "name": ext_data.get("name", f"Token {nft_data.get('token_id')}"),
                    "image": image,
                    "tokenId": nft_data.get("token_id"),
                    "contract": item.get("contract_address")
                })
        return nfts
    except:
        return None

def try_moralis():
    key = os.getenv("MORALIS_API_KEY")
    if not key: return None
    url = f"https://deep-index.moralis.io/api/v2/{WALLET}/nft?chain=polygon&limit=100"
    headers = {"X-API-Key": key}
    try:
        r = requests.get(url, headers=headers, timeout=10)
        if r.status_code != 200: return None
        data = r.json()
        nfts = []
        for nft in data.get("result", []):
            meta = nft.get("normalized_metadata") or nft.get("metadata")
            if isinstance(meta, str):
                try:
                    meta = json.loads(meta)
                except:
                    meta = {}
            image = meta.get("image", "") if meta else ""
            if image.startswith("ipfs://"):
                image = image.replace("ipfs://", "https://ipfs.io/ipfs/")
            nfts.append({
                "name": nft.get("name") or meta.get("name", f"Token {nft.get('token_id')}"),
                "image": image,
                "tokenId": nft.get("token_id"),
                "contract": nft.get("token_address")
            })
        return nfts
    except:
        return None

def generate_html(nfts):
    cards = ""
    for nft in nfts:
        name = nft.get("name", "Unknown")[:50]
        img = nft.get("image") or "https://via.placeholder.com/250?text=No+Image"
        tid = nft.get("tokenId")
        contract = nft.get("contract")
        opensea_url = f"https://opensea.io/assets/polygon/{contract}/{tid}"
        cards += f'''
        <div class="nft-card">
            <img src="{img}" alt="{name}">
            <h3>{name}</h3>
            <p>Token ID: {tid}</p>
            <a href="{opensea_url}" target="_blank">View on OpenSea</a>
        </div>
        '''
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
    <div class="gallery">{cards}</div>
    <div class="ad">
        🔥 <a href="https://korerussbiz.com/merch" target="_blank">Get your NFT printed on a T‑Shirt! Limited time offer.</a> 🔥
    </div>
</body>
</html>'''
    return html

def main():
    print("Trying to fetch NFTs using available API keys...")
    nfts = try_polygonscan()
    if nfts:
        print("✅ Used Polygonscan API")
    else:
        print("Polygonscan failed, trying OpenSea...")
        nfts = try_opensea()
        if nfts:
            print("✅ Used OpenSea API")
    if not nfts:
        print("OpenSea failed, trying Covalent...")
        nfts = try_covalent()
        if nfts:
            print("✅ Used Covalent API")
    if not nfts:
        print("Covalent failed, trying Moralis...")
        nfts = try_moralis()
        if nfts:
            print("✅ Used Moralis API")
    if not nfts:
        print("All APIs failed. Creating placeholder gallery.")
        nfts = []
    html = generate_html(nfts)
    with open(OUTPUT, "w") as f:
        f.write(html)
    print(f"Gallery written to {OUTPUT} with {len(nfts)} NFTs.")

if __name__ == "__main__":
    main()
