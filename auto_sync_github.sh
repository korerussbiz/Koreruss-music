#!/bin/bash
# Auto-sync Termux to GitHub - Earn while offline
# This script automatically updates your GitHub site with monetization content

REPO_DIR="/sdcard/Download"
GITHUB_REPO="https://github.com/korerussbiz/Koreruss-music.git"
SITE_URL="https://koreruss-music.onrender.com"

cd $REPO_DIR

# Initialize git if needed
if [ ! -d ".git" ]; then
    git init
    git remote add origin $GITHUB_REPO
fi

# Pull latest changes
git pull origin main --rebase 2>/dev/null

# Add all changes
git add .

# Create commit with timestamp
TIMESTAMP=$(date '+%Y-%m-%d %H:%M:%S')
git commit -m "Auto-update: $TIMESTAMP - Monetization content sync"

# Push to GitHub
git push origin main

echo "✅ Synced to GitHub at $TIMESTAMP"
echo "🌐 Site will update at: $SITE_URL"
echo "💰 All monetization features active"
