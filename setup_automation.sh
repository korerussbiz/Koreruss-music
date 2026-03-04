#!/bin/bash
# Cron Job Setup for Automated Traffic
# This will run traffic automation every hour

SCRIPT_DIR="/sdcard/Download"

# Install cron if not available
if ! command -v cron &> /dev/null; then
    echo "Installing cron..."
    pkg install cronie -y
fi

# Make scripts executable
chmod +x $SCRIPT_DIR/auto_traffic.sh

# Add to crontab (runs every hour)
(crontab -l 2>/dev/null; echo "0 * * * * bash $SCRIPT_DIR/auto_traffic.sh") | crontab -

# Add Node.js bot to run on startup
(crontab -l 2>/dev/null; echo "@reboot cd $SCRIPT_DIR && node traffic_bot.js &") | crontab -

echo "✅ Cron jobs installed!"
echo "📋 Current crontab:"
crontab -l

echo ""
echo "🚀 AUTOMATION ACTIVE:"
echo "- Bash script runs every hour"
echo "- Node.js bot runs continuously"
echo "- Logs saved to traffic_log.txt"
echo ""
echo "To start Node.js bot now:"
echo "cd $SCRIPT_DIR && node traffic_bot.js &"
