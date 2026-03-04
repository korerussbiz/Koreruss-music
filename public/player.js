// Persistent Music Player - Works across all pages
const MUSIC_SERVER = 'https://ancient-swan-53.loca.lt';
let allSongs = [];
let currentIndex = 0;
let isMuted = false;

// Load songs from server
async function loadSongs() {
  try {
    const response = await fetch(MUSIC_SERVER + '/api/songs', {
      headers: { 'Bypass-Tunnel-Reminder': 'true' }
    });
    const data = await response.json();
    allSongs = data.songs;
    
    // Save to localStorage for persistence
    localStorage.setItem('koreruss_songs', JSON.stringify(allSongs));
    localStorage.setItem('koreruss_songs_loaded', Date.now());
    
    updateTrackDisplay();
    
    // Auto-play if not already playing
    const player = document.getElementById('musicPlayer');
    if (!player.src && allSongs.length > 0) {
      playRandom();
    }
    
    return allSongs;
  } catch (error) {
    console.error('Failed to load songs:', error);
    
    // Try to load from localStorage
    const cached = localStorage.getItem('koreruss_songs');
    if (cached) {
      allSongs = JSON.parse(cached);
      updateTrackDisplay();
    }
    
    return allSongs;
  }
}

// Play specific song by index
function playSongByIndex(index) {
  currentIndex = index;
  playSong(index);
  
  // Update visual state
  document.querySelectorAll('.song-card').forEach((card, i) => {
    card.classList.toggle('playing', i === index);
  });
}

// Play song
function playSong(index) {
  if (allSongs.length === 0) return;
  
  const song = allSongs[index];
  const player = document.getElementById('musicPlayer');
  
  player.src = MUSIC_SERVER + song.url;
  player.play().catch(e => console.log('Autoplay blocked'));
  
  // Save current state
  localStorage.setItem('koreruss_current_index', index);
  localStorage.setItem('koreruss_current_time', 0);
  
  updateTrackDisplay();
}

// Update track display
function updateTrackDisplay() {
  const display = document.getElementById('currentTrack');
  if (!display) return;
  
  if (allSongs.length === 0) {
    display.innerHTML = '<i class="fas fa-music"></i> Loading songs...';
    return;
  }
  
  const song = allSongs[currentIndex];
  display.innerHTML = `
    <i class="fas fa-music"></i> Now Playing: <strong>${song.name}</strong>
    <span style="opacity:0.7;margin-left:10px">(${currentIndex + 1} of ${allSongs.length})</span>
  `;
}

// Play random song
function playRandom() {
  if (allSongs.length === 0) return;
  currentIndex = Math.floor(Math.random() * allSongs.length);
  playSong(currentIndex);
}

// Play next song
function playNext() {
  if (allSongs.length === 0) return;
  currentIndex = (currentIndex + 1) % allSongs.length;
  playSong(currentIndex);
}

// Play previous song
function playPrevious() {
  if (allSongs.length === 0) return;
  currentIndex = (currentIndex - 1 + allSongs.length) % allSongs.length;
  playSong(currentIndex);
}

// Toggle mute
function toggleMute() {
  const player = document.getElementById('musicPlayer');
  const icon = document.getElementById('volumeIcon');
  
  isMuted = !isMuted;
  player.muted = isMuted;
  
  icon.className = isMuted ? 'fas fa-volume-mute' : 'fas fa-volume-up';
}

// Auto-play next when song ends
document.addEventListener('DOMContentLoaded', () => {
  const player = document.getElementById('musicPlayer');
  
  if (player) {
    player.addEventListener('ended', playNext);
    
    // Save playback position periodically
    player.addEventListener('timeupdate', () => {
      if (player.currentTime > 0) {
        localStorage.setItem('koreruss_current_time', player.currentTime);
      }
    });
    
    // Restore previous state
    const savedIndex = localStorage.getItem('koreruss_current_index');
    const savedTime = localStorage.getItem('koreruss_current_time');
    
    if (savedIndex && allSongs.length > 0) {
      currentIndex = parseInt(savedIndex);
      updateTrackDisplay();
    }
  }
  
  // Load songs on page load
  loadSongs();
});

// Keep player state when navigating
window.addEventListener('beforeunload', () => {
  const player = document.getElementById('musicPlayer');
  if (player) {
    localStorage.setItem('koreruss_current_time', player.currentTime);
    localStorage.setItem('koreruss_current_index', currentIndex);
  }
});
