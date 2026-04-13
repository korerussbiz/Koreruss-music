const fs = require('fs');
const path = require('path');
const axios = require('axios');
const { ethers } = require('ethers');
require('dotenv').config({ path: path.join(require('os').homedir(), 'koreruss.env') });

const CONTRACT = "0x72c997ED37F786829F01f6a73B14F6Bdd61c2B94";
// Use the RPC from your env, or fallback to a working public one
const RPC_URL = process.env.RPC_URL || "https://1rpc.io/matic";
const provider = new ethers.JsonRpcProvider(RPC_URL);
const abi = ["function tokenURI(uint256) view returns (string)"];

// List of token IDs you know exist (from your minting history)
// If you don't know, we'll scan from 1 to 100
const KNOWN_TOKENS = [1,2,3,4,5,6,7,8,9,10,34,35,36,37]; // add more if needed

async function fetchNFTs() {
    const contract = new ethers.Contract(CONTRACT, abi, provider);
    const nfts = [];
    for (const tokenId of KNOWN_TOKENS) {
        try {
            const uri = await contract.tokenURI(tokenId);
            if (!uri) continue;
            console.log(`✅ Token ${tokenId}: ${uri}`);
            const metaUrl = uri.replace('ipfs://', 'https://ipfs.io/ipfs/');
            const metaRes = await axios.get(metaUrl, { timeout: 10000 });
            const meta = metaRes.data;
            let image = meta.image || meta.animation_url || "";
            if (image.startsWith('ipfs://')) image = image.replace('ipfs://', 'https://ipfs.io/ipfs/');
            nfts.push({
                tokenId,
                name: meta.name || `Token ${tokenId}`,
                image: image || "https://via.placeholder.com/250",
                contract: CONTRACT
            });
        } catch (err) {
            console.log(`⚠️ Token ${tokenId} failed: ${err.message}`);
        }
    }
    return nfts;
}

function generateHTML(nfts) {
    let cards = '';
    for (const nft of nfts) {
        cards += `
        <div class="nft-card">
            <img src="${nft.image}" alt="${nft.name}" onerror="this.src='https://via.placeholder.com/250'">
            <h3>${nft.name.substring(0, 50)}</h3>
            <p>Token ID: ${nft.tokenId}</p>
            <a href="https://opensea.io/assets/polygon/${nft.contract}/${nft.tokenId}" target="_blank">View on OpenSea</a>
        </div>`;
    }
    return `<!DOCTYPE html>
<html>
<head>
    <title>Koreruss NFT Gallery</title>
    <meta charset="UTF-8">
    <style>
        body { font-family: Arial; margin: 20px; background: #f5f5f5; text-align: center; }
        .gallery { display: flex; flex-wrap: wrap; justify-content: center; gap: 20px; margin-top: 20px; }
        .nft-card { background: white; width: 250px; padding: 10px; border-radius: 10px; box-shadow: 0 2px 8px rgba(0,0,0,0.1); }
        .nft-card img { width: 100%; border-radius: 8px; max-height: 250px; object-fit: contain; }
        .nft-card h3 { font-size: 1em; margin: 10px 0; }
        .nft-card a { display: inline-block; margin-top: 10px; padding: 5px 10px; background: #2081e2; color: white; text-decoration: none; border-radius: 5px; }
        .ad { margin: 30px auto; max-width: 728px; background: #e0e0e0; padding: 15px; border-radius: 8px; }
        .ad a { color: #2081e2; font-weight: bold; text-decoration: none; }
    </style>
</head>
<body>
    <h1>Koreruss NFT Collection</h1>
    <div class="gallery">${cards}</div>
    <div class="ad">
        🔥 <a href="/merch.html" target="_blank">Get your NFT printed on a T‑Shirt! Limited time offer.</a> 🔥
    </div>
</body>
</html>`;
}

async function main() {
    console.log(`Using RPC: ${RPC_URL}`);
    const nfts = await fetchNFTs();
    if (nfts.length === 0) {
        console.error("No NFTs found. Please add your token IDs to the KNOWN_TOKENS list.");
        process.exit(1);
    }
    const html = generateHTML(nfts);
    fs.writeFileSync('public/nft-gallery.html', html);
    console.log(`✅ Gallery written to public/nft-gallery.html with ${nfts.length} NFTs.`);
}
main().catch(console.error);
