const { execSync } = require('child_process');
const fs = require('fs');
const path = require('path');

// Configuration
const REPO_DIR = '/sdcard/Download';
const GITHUB_REPO = 'https://github.com/korerussbiz/Koreruss-music.git';
const SYNC_INTERVAL = 30 * 60 * 1000; // 30 minutes
const LOG_FILE = path.join(REPO_DIR, 'auto_sync.log');

// Log function
function log(message) {
    const timestamp = new Date().toISOString();
    const logMessage = `[${timestamp}] ${message}\n`;
    fs.appendFileSync(LOG_FILE, logMessage);
    console.log(message);
}

// Collect monetization data from Termux
function collectMonetizationData() {
    log('📊 Collecting monetization data...');
    
    const data = {
        timestamp: new Date().toISOString(),
        affiliate_links: 25,
        ad_networks: ['AdSense', 'Adsterra'],
        music_tracks: 3,
        video_count: 3,
        crypto_wallets: {
            btc: 'bc1qleqcqp30tcn0l6rl08v6569jxfxrglfzefgnfa',
            eth: '0xCf974b9e14766f839D8C59bDA1D4Dff3CF3f8b33'
        },
        pricing: {
            single: 4.99,
            album: 49.99,
            exclusive: 499.99
        }
    };
    
    // Save data to JSON
    fs.writeFileSync(
        path.join(REPO_DIR, 'public', 'monetization_data.json'),
        JSON.stringify(data, null, 2)
    );
    
    log('✅ Monetization data collected');
    return data;
}

// Update site with latest info
function updateSiteContent() {
    log('🔄 Updating site content...');
    
    try {
        // Collect latest data
        const data = collectMonetizationData();
        
        // Update timestamp in HTML
        const indexPath = path.join(REPO_DIR, 'public', 'index.html');
        let html = fs.readFileSync(indexPath, 'utf8');
        
        // Add last update timestamp
        const updateBadge = `<!-- Last Auto-Update: ${data.timestamp} -->`;
        if (!html.includes('Last Auto-Update')) {
            html = html.replace('</head>', `${updateBadge}\n</head>`);
            fs.writeFileSync(indexPath, html);
        }
        
        log('✅ Site content updated');
    } catch (error) {
        log('❌ Update error: ' + error.message);
    }
}

// Sync to GitHub
function syncToGitHub() {
    log('🚀 Syncing to GitHub...');
    
    try {
        process.chdir(REPO_DIR);
        
        // Git commands
        execSync('git add .', { stdio: 'pipe' });
        
        const timestamp = new Date().toLocaleString();
        const commitMsg = `Auto-sync: ${timestamp} - Monetization update`;
        execSync(`git commit -m "${commitMsg}"`, { stdio: 'pipe' });
        
        execSync('git push origin main', { stdio: 'pipe' });
        
        log('✅ Synced to GitHub successfully');
        log('🌐 Render will auto-deploy in 2-3 minutes');
        log('💰 All monetization features will be live');
    } catch (error) {
        if (error.message.includes('nothing to commit')) {
            log('ℹ️  No changes to sync');
        } else {
            log('❌ Sync error: ' + error.message);
        }
    }
}

// Main sync function
function performSync() {
    log('═══════════════════════════════════════');
    log('🔄 Starting auto-sync cycle...');
    
    updateSiteContent();
    syncToGitHub();
    
    log('✅ Sync cycle complete');
    log(`⏰ Next sync in ${SYNC_INTERVAL / 60000} minutes`);
    log('═══════════════════════════════════════\n');
}

// Run immediately
performSync();

// Schedule regular syncs
setInterval(performSync, SYNC_INTERVAL);

log('🤖 Auto-sync bot started');
log(`📅 Syncing every ${SYNC_INTERVAL / 60000} minutes`);
log('💰 Earning while you sleep!');
