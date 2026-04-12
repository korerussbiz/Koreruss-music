export default async function handler(req, res) {
  const walletAddress = "0xCf974b9e14766f839D8C59bDA1D4Dff3CF3f8b33";

  // Helper to try each provider
  async function tryCovalent(key) {
    if (!key) return null;
    const url = `https://api.covalenthq.com/v1/137/address/${walletAddress}/balances_v2/?nft=true&key=${key}`;
    try {
      const r = await fetch(url);
      if (!r.ok) return null;
      const d = await r.json();
      const nfts = d.data.items.filter(i => i.type === 'nft');
      return nfts.map(nft => {
        const nd = nft.nft_data[0];
        return {
          name: nd?.external_data?.name || `Token ${nd?.token_id}`,
          image: (nd?.external_data?.image || '').replace('ipfs://', 'https://ipfs.io/ipfs/'),
          tokenId: nd?.token_id,
          contract: nft.contract_address,
        };
      });
    } catch { return null; }
  }

  async function tryMoralis(key) {
    if (!key) return null;
    const url = `https://deep-index.moralis.io/api/v2/${walletAddress}/nft?chain=polygon&limit=100`;
    try {
      const r = await fetch(url, { headers: { 'X-API-Key': key } });
      if (!r.ok) return null;
      const d = await r.json();
      return d.result.map(nft => ({
        name: nft.name || `Token ${nft.token_id}`,
        image: (nft.normalized_metadata?.image || nft.metadata?.image || '').replace('ipfs://', 'https://ipfs.io/ipfs/'),
        tokenId: nft.token_id,
        contract: nft.token_address,
      }));
    } catch { return null; }
  }

  async function tryAlchemy(key) {
    if (!key) return null;
    const url = `https://polygon-mainnet.g.alchemy.com/nft/v2/${key}/getNFTsForOwner?owner=${walletAddress}&withMetadata=true`;
    try {
      const r = await fetch(url);
      if (!r.ok) return null;
      const d = await r.json();
      return d.ownedNfts.map(nft => ({
        name: nft.title || nft.contract.name,
        image: nft.media?.[0]?.gateway || nft.metadata?.image?.replace('ipfs://', 'https://ipfs.io/ipfs/'),
        tokenId: nft.id.tokenId,
        contract: nft.contract.address,
      }));
    } catch { return null; }
  }

  async function tryInfura(key) {
    if (!key) return null;
    const url = `https://nft.api.infura.io/networks/polygon-mainnet/accounts/${walletAddress}/assets/nfts`;
    try {
      const r = await fetch(url, { headers: { 'Authorization': `Bearer ${key}` } });
      if (!r.ok) return null;
      const d = await r.json();
      return d.assets.map(nft => ({
        name: nft.name,
        image: nft.image_url,
        tokenId: nft.token_id,
        contract: nft.contract_address,
      }));
    } catch { return null; }
  }

  async function tryOpenSea() {
    const url = `https://api.opensea.io/api/v2/chain/polygon/account/${walletAddress}/nfts?limit=50`;
    try {
      const r = await fetch(url);
      if (!r.ok) return null;
      const d = await r.json();
      return d.nfts.map(nft => ({
        name: nft.name || `Token ${nft.identifier}`,
        image: nft.display_image_url || nft.image_url,
        tokenId: nft.identifier,
        contract: nft.contract,
      }));
    } catch { return null; }
  }

  // Order: Covalent, Moralis, Alchemy, Infura, then OpenSea
  let nfts = await tryCovalent(process.env.COVALENT_API_KEY);
  if (!nfts) nfts = await tryMoralis(process.env.MORALIS_API_KEY);
  if (!nfts) nfts = await tryAlchemy(process.env.ALCHEMY_API_KEY);
  if (!nfts) nfts = await tryInfura(process.env.INFURA_PROJECT_ID);
  if (!nfts) nfts = await tryOpenSea();

  if (!nfts) {
    return res.status(500).json({ error: 'No API key worked and OpenSea fallback failed.' });
  }

  // Cache for 5 minutes
  res.setHeader('Cache-Control', 's-maxage=300');
  res.status(200).json({ nfts });
}
