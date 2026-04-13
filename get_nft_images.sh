#!/bin/bash
WALLET="0xCf974b9e14766f839D8C59bDA1D4Dff3CF3f8b33"
curl -s "https://api.opensea.io/api/v2/chain/polygon/account/${WALLET}/nfts" | jq -r '.nfts[] | "\(.identifier) | \(.display_image_url)"'
