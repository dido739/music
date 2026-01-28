// Music Server Frontend Application

const API_BASE = '/api';

// Application State
const state = {
    currentTrack: null,
    queue: [],
    queueIndex: -1,
    isPlaying: false,
    shuffle: false,
    repeat: false,
    volume: 0.7,
    tracks: [],
    playlists: [],
    currentPage: 1,
    totalPages: 1,
    currentPlaylist: null,
    theme: localStorage.getItem('theme') || 'dark'
};

// Initialize the app
document.addEventListener('DOMContentLoaded', () => {
    initializeApp();
});

function initializeApp() {
    setupEventListeners();
    applyTheme();
    loadStats();
    loadTracks();
    loadPlaylists();
    setupPlayer();
}

// Event Listeners
function setupEventListeners() {
    // Navigation
    document.querySelectorAll('.nav-item').forEach(item => {
        item.addEventListener('click', (e) => {
            e.preventDefault();
            const page = item.dataset.page;
            navigateToPage(page);
        });
    });

    // Search
    const searchInput = document.getElementById('search-input');
    let searchTimeout;
    searchInput.addEventListener('input', (e) => {
        clearTimeout(searchTimeout);
        searchTimeout = setTimeout(() => {
            searchTracks(e.target.value);
        }, 300);
    });

    // Theme toggle
    document.getElementById('theme-toggle').addEventListener('click', toggleTheme);

    // Scan library
    document.getElementById('scan-btn').addEventListener('click', scanLibrary);

    // Sort
    document.getElementById('sort-by').addEventListener('change', (e) => {
        loadTracks(1, e.target.value);
    });

    // Create playlist
    document.getElementById('create-playlist-btn').addEventListener('click', showCreatePlaylistModal);
    document.getElementById('save-playlist-btn').addEventListener('click', createPlaylist);
    document.getElementById('cancel-playlist-btn').addEventListener('click', hideCreatePlaylistModal);

    // Downloads
    document.getElementById('youtube-download-btn').addEventListener('click', downloadYouTube);
    document.getElementById('spotify-download-btn').addEventListener('click', downloadSpotify);

    // Settings
    document.getElementById('add-directory-btn').addEventListener('click', addDirectory);
    document.getElementById('theme-select').addEventListener('change', (e) => {
        state.theme = e.target.value;
        applyTheme();
    });

    // Player controls
    document.getElementById('play-pause-btn').addEventListener('click', togglePlayPause);
    document.getElementById('prev-btn').addEventListener('click', playPrevious);
    document.getElementById('next-btn').addEventListener('click', playNext);
    document.getElementById('shuffle-btn').addEventListener('click', toggleShuffle);
    document.getElementById('repeat-btn').addEventListener('click', toggleRepeat);
    document.getElementById('volume-btn').addEventListener('click', toggleMute);
    document.getElementById('volume-slider').addEventListener('input', (e) => {
        setVolume(e.target.value / 100);
    });

    // Audio player events
    const audio = document.getElementById('audio-player');
    audio.addEventListener('timeupdate', updateProgress);
    audio.addEventListener('ended', onTrackEnded);
    audio.addEventListener('loadedmetadata', onTrackLoaded);

    // Seek bar
    document.getElementById('seek-bar').addEventListener('input', (e) => {
        const audio = document.getElementById('audio-player');
        audio.currentTime = (e.target.value / 100) * audio.duration;
    });
}

// Navigation
function navigateToPage(page) {
    // Update nav items
    document.querySelectorAll('.nav-item').forEach(item => {
        item.classList.remove('active');
        if (item.dataset.page === page) {
            item.classList.add('active');
        }
    });

    // Update pages
    document.querySelectorAll('.page').forEach(p => {
        p.classList.remove('active');
    });
    document.getElementById(`${page}-page`).classList.add('active');

    // Load page data
    if (page === 'library') {
        loadTracks();
    } else if (page === 'playlists') {
        loadPlaylists();
    } else if (page === 'downloads') {
        loadDownloads();
    } else if (page === 'settings') {
        loadSettings();
    }
}

// Theme
function applyTheme() {
    document.body.setAttribute('data-theme', state.theme);
    localStorage.setItem('theme', state.theme);
    
    const themeIcon = document.querySelector('#theme-toggle i');
    themeIcon.className = state.theme === 'dark' ? 'fas fa-sun' : 'fas fa-moon';
    
    document.getElementById('theme-select').value = state.theme;
}

function toggleTheme() {
    state.theme = state.theme === 'dark' ? 'light' : 'dark';
    applyTheme();
}

// API Calls
async function api(endpoint, options = {}) {
    try {
        const response = await fetch(`${API_BASE}${endpoint}`, {
            ...options,
            headers: {
                'Content-Type': 'application/json',
                ...options.headers
            }
        });
        
        if (!response.ok) {
            throw new Error(`API error: ${response.statusText}`);
        }
        
        return await response.json();
    } catch (error) {
        console.error('API call failed:', error);
        throw error;
    }
}

// Stats
async function loadStats() {
    try {
        const stats = await api('/stats');
        document.getElementById('total-tracks').textContent = stats.total_tracks || 0;
        document.getElementById('total-artists').textContent = stats.total_artists || 0;
        document.getElementById('total-albums').textContent = stats.total_albums || 0;
    } catch (error) {
        console.error('Failed to load stats:', error);
    }
}

// Tracks
async function loadTracks(page = 1, sortBy = 'title') {
    try {
        const data = await api(`/tracks?page=${page}&per_page=50&sort_by=${sortBy}`);
        state.tracks = data.tracks;
        state.currentPage = data.page;
        state.totalPages = data.pages;
        
        renderTracks(data.tracks);
        renderPagination(data.page, data.pages);
    } catch (error) {
        console.error('Failed to load tracks:', error);
    }
}

function renderTracks(tracks) {
    const grid = document.getElementById('tracks-grid');
    grid.innerHTML = '';
    
    if (tracks.length === 0) {
        grid.innerHTML = '<p style="grid-column: 1/-1; text-align: center; padding: 40px; color: var(--text-secondary);">No tracks found. Click "Scan Library" to add music.</p>';
        return;
    }
    
    tracks.forEach(track => {
        const card = document.createElement('div');
        card.className = 'track-card';
        card.onclick = () => playTrack(track);
        
        const albumArt = track.cover_art ? `/api/tracks/${track.id}/stream` : '';
        
        card.innerHTML = `
            <img src="${albumArt || 'data:image/svg+xml,<svg xmlns="http://www.w3.org/2000/svg"/>'}" 
                 alt="Album Art" 
                 class="track-album-art"
                 onerror="this.src='data:image/svg+xml,<svg xmlns=%22http://www.w3.org/2000/svg%22><rect width=%22100%%22 height=%22100%%22 fill=%22%232f2f2f%22/><text x=%2250%%22 y=%2250%%22 text-anchor=%22middle%22 dy=%22.3em%22 fill=%22%23666%22 font-size=%2240%22>♪</text></svg>'">
            <div class="track-info">
                <div class="track-title">${escapeHtml(track.title || 'Unknown')}</div>
                <div class="track-artist">${escapeHtml(track.artist || 'Unknown Artist')}</div>
                <div class="track-duration">${formatDuration(track.duration)}</div>
            </div>
            <div class="track-actions">
                <button class="favorite-btn ${track.favorite ? 'active' : ''}" 
                        onclick="event.stopPropagation(); toggleFavorite(${track.id})">
                    <i class="fas fa-heart"></i>
                </button>
            </div>
        `;
        
        grid.appendChild(card);
    });
}

function renderPagination(current, total) {
    const pagination = document.getElementById('pagination');
    pagination.innerHTML = '';
    
    if (total <= 1) return;
    
    const prev = document.createElement('button');
    prev.textContent = 'Previous';
    prev.disabled = current === 1;
    prev.onclick = () => loadTracks(current - 1);
    pagination.appendChild(prev);
    
    const info = document.createElement('span');
    info.textContent = `Page ${current} of ${total}`;
    info.style.margin = '0 15px';
    pagination.appendChild(info);
    
    const next = document.createElement('button');
    next.textContent = 'Next';
    next.disabled = current === total;
    next.onclick = () => loadTracks(current + 1);
    pagination.appendChild(next);
}

async function searchTracks(query) {
    if (!query) {
        loadTracks();
        return;
    }
    
    try {
        const data = await api(`/search?q=${encodeURIComponent(query)}`);
        renderTracks(data.tracks);
        document.getElementById('pagination').innerHTML = '';
    } catch (error) {
        console.error('Search failed:', error);
    }
}

async function toggleFavorite(trackId) {
    try {
        await api(`/tracks/${trackId}/favorite`, { method: 'POST' });
        loadTracks(state.currentPage);
    } catch (error) {
        console.error('Failed to toggle favorite:', error);
    }
}

// Playlists
async function loadPlaylists() {
    try {
        const playlists = await api('/playlists');
        state.playlists = playlists;
        renderPlaylists(playlists);
    } catch (error) {
        console.error('Failed to load playlists:', error);
    }
}

function renderPlaylists(playlists) {
    const grid = document.getElementById('playlists-grid');
    grid.innerHTML = '';
    
    if (playlists.length === 0) {
        grid.innerHTML = '<p style="grid-column: 1/-1; text-align: center; padding: 40px; color: var(--text-secondary);">No playlists yet. Create one to get started!</p>';
        return;
    }
    
    playlists.forEach(playlist => {
        const card = document.createElement('div');
        card.className = 'playlist-card';
        card.onclick = () => openPlaylist(playlist.id);
        
        card.innerHTML = `
            <div class="playlist-name">${escapeHtml(playlist.name)}</div>
            <div class="playlist-tracks-count">${playlist.track_count} tracks</div>
        `;
        
        grid.appendChild(card);
    });
}

function showCreatePlaylistModal() {
    document.getElementById('playlist-modal').classList.add('active');
    document.getElementById('playlist-name').value = '';
    document.getElementById('playlist-description').value = '';
}

function hideCreatePlaylistModal() {
    document.getElementById('playlist-modal').classList.remove('active');
}

async function createPlaylist() {
    const name = document.getElementById('playlist-name').value;
    const description = document.getElementById('playlist-description').value;
    
    if (!name) {
        alert('Please enter a playlist name');
        return;
    }
    
    try {
        await api('/playlists', {
            method: 'POST',
            body: JSON.stringify({ name, description })
        });
        
        hideCreatePlaylistModal();
        loadPlaylists();
    } catch (error) {
        console.error('Failed to create playlist:', error);
        alert('Failed to create playlist');
    }
}

async function openPlaylist(playlistId) {
    try {
        const playlist = await api(`/playlists/${playlistId}`);
        state.currentPlaylist = playlist;
        
        // Show playlist tracks (simplified - in a full app, this would be a separate view)
        alert(`Playlist: ${playlist.name}\nTracks: ${playlist.tracks.length}`);
    } catch (error) {
        console.error('Failed to load playlist:', error);
    }
}

// Scanner
async function scanLibrary() {
    const btn = document.getElementById('scan-btn');
    btn.disabled = true;
    btn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Scanning...';
    
    try {
        await api('/scan/start', { method: 'POST' });
        
        // Poll for progress
        const interval = setInterval(async () => {
            const progress = await api('/scan/progress');
            
            if (progress.scanned >= progress.total && progress.total > 0) {
                clearInterval(interval);
                btn.disabled = false;
                btn.innerHTML = '<i class="fas fa-sync"></i> Scan Library';
                loadTracks();
                loadStats();
            }
        }, 1000);
    } catch (error) {
        console.error('Scan failed:', error);
        btn.disabled = false;
        btn.innerHTML = '<i class="fas fa-sync"></i> Scan Library';
    }
}

// Downloads
async function downloadYouTube() {
    const url = document.getElementById('youtube-url').value;
    const format = document.getElementById('youtube-format').value;
    const quality = document.getElementById('youtube-quality').value;
    
    if (!url) {
        alert('Please enter a YouTube URL');
        return;
    }
    
    try {
        await api('/download/youtube', {
            method: 'POST',
            body: JSON.stringify({ url, format, quality: parseInt(quality) })
        });
        
        alert('Download started! Check the download history below.');
        document.getElementById('youtube-url').value = '';
        
        setTimeout(loadDownloads, 1000);
    } catch (error) {
        console.error('Download failed:', error);
        alert('Failed to start download');
    }
}

async function downloadSpotify() {
    const url = document.getElementById('spotify-url').value;
    
    if (!url) {
        alert('Please enter a Spotify URL');
        return;
    }
    
    try {
        await api('/download/spotify', {
            method: 'POST',
            body: JSON.stringify({ url })
        });
        
        alert('Download started! Check the download history below.');
        document.getElementById('spotify-url').value = '';
        
        setTimeout(loadDownloads, 1000);
    } catch (error) {
        console.error('Download failed:', error);
        alert('Failed to start download');
    }
}

async function loadDownloads() {
    try {
        const downloads = await api('/downloads');
        renderDownloads(downloads);
    } catch (error) {
        console.error('Failed to load downloads:', error);
    }
}

function renderDownloads(downloads) {
    const list = document.getElementById('download-list');
    list.innerHTML = '';
    
    const allDownloads = [
        ...Object.entries(downloads.youtube || {}).map(([id, d]) => ({ ...d, id, type: 'YouTube' })),
        ...Object.entries(downloads.spotify || {}).map(([id, d]) => ({ ...d, id, type: 'Spotify' }))
    ];
    
    if (allDownloads.length === 0) {
        list.innerHTML = '<p style="text-align: center; padding: 20px; color: var(--text-secondary);">No downloads yet</p>';
        return;
    }
    
    allDownloads.forEach(download => {
        const item = document.createElement('div');
        item.className = 'download-item';
        
        item.innerHTML = `
            <div class="download-info">
                <div>${download.type}</div>
                <div class="download-url">${escapeHtml(download.url)}</div>
                <div class="download-status">${download.status} ${download.progress ? `(${download.progress.toFixed(1)}%)` : ''}</div>
            </div>
            <div class="download-progress">
                <div class="download-progress-bar" style="width: ${download.progress || 0}%"></div>
            </div>
        `;
        
        list.appendChild(item);
    });
}

// Settings
async function loadSettings() {
    try {
        const config = await api('/config');
        renderDirectories(config.music_directories || []);
    } catch (error) {
        console.error('Failed to load settings:', error);
    }
}

function renderDirectories(directories) {
    const list = document.getElementById('directories-list');
    list.innerHTML = '';
    
    directories.forEach(dir => {
        const item = document.createElement('div');
        item.className = 'directory-item';
        
        item.innerHTML = `
            <span>${escapeHtml(dir)}</span>
            <button class="btn btn-icon" onclick="removeDirectory('${escapeHtml(dir)}')">
                <i class="fas fa-trash"></i>
            </button>
        `;
        
        list.appendChild(item);
    });
}

async function addDirectory() {
    const directory = document.getElementById('new-directory').value;
    
    if (!directory) {
        alert('Please enter a directory path');
        return;
    }
    
    try {
        await api('/config/directories', {
            method: 'POST',
            body: JSON.stringify({ directory })
        });
        
        document.getElementById('new-directory').value = '';
        loadSettings();
    } catch (error) {
        console.error('Failed to add directory:', error);
        alert('Failed to add directory');
    }
}

async function removeDirectory(directory) {
    if (!confirm(`Remove directory: ${directory}?`)) {
        return;
    }
    
    try {
        await api('/config/directories', {
            method: 'DELETE',
            body: JSON.stringify({ directory })
        });
        
        loadSettings();
    } catch (error) {
        console.error('Failed to remove directory:', error);
        alert('Failed to remove directory');
    }
}

// Player
function setupPlayer() {
    const audio = document.getElementById('audio-player');
    audio.volume = state.volume;
    document.getElementById('volume-slider').value = state.volume * 100;
}

function playTrack(track) {
    state.currentTrack = track;
    state.queue = [track];
    state.queueIndex = 0;
    
    const audio = document.getElementById('audio-player');
    audio.src = `/api/tracks/${track.id}/stream`;
    audio.play();
    
    state.isPlaying = true;
    updatePlayerUI();
    updatePlayButton();
    
    // Mark as played
    api(`/tracks/${track.id}/play`, { method: 'POST' });
}

function togglePlayPause() {
    const audio = document.getElementById('audio-player');
    
    if (state.isPlaying) {
        audio.pause();
        state.isPlaying = false;
    } else {
        audio.play();
        state.isPlaying = true;
    }
    
    updatePlayButton();
}

function playNext() {
    if (state.queue.length === 0) return;
    
    let nextIndex = state.queueIndex + 1;
    
    if (nextIndex >= state.queue.length) {
        if (state.repeat) {
            nextIndex = 0;
        } else {
            return;
        }
    }
    
    state.queueIndex = nextIndex;
    playTrack(state.queue[nextIndex]);
}

function playPrevious() {
    if (state.queue.length === 0) return;
    
    const audio = document.getElementById('audio-player');
    
    if (audio.currentTime > 3) {
        audio.currentTime = 0;
    } else {
        let prevIndex = state.queueIndex - 1;
        
        if (prevIndex < 0) {
            prevIndex = state.queue.length - 1;
        }
        
        state.queueIndex = prevIndex;
        playTrack(state.queue[prevIndex]);
    }
}

function toggleShuffle() {
    state.shuffle = !state.shuffle;
    document.getElementById('shuffle-btn').classList.toggle('active', state.shuffle);
}

function toggleRepeat() {
    state.repeat = !state.repeat;
    document.getElementById('repeat-btn').classList.toggle('active', state.repeat);
}

function toggleMute() {
    const audio = document.getElementById('audio-player');
    const btn = document.getElementById('volume-btn');
    const icon = btn.querySelector('i');
    
    if (audio.volume > 0) {
        state.prevVolume = audio.volume;
        audio.volume = 0;
        document.getElementById('volume-slider').value = 0;
        icon.className = 'fas fa-volume-mute';
    } else {
        audio.volume = state.prevVolume || 0.7;
        document.getElementById('volume-slider').value = audio.volume * 100;
        icon.className = 'fas fa-volume-up';
    }
}

function setVolume(volume) {
    const audio = document.getElementById('audio-player');
    audio.volume = volume;
    state.volume = volume;
    
    const icon = document.querySelector('#volume-btn i');
    if (volume === 0) {
        icon.className = 'fas fa-volume-mute';
    } else if (volume < 0.5) {
        icon.className = 'fas fa-volume-down';
    } else {
        icon.className = 'fas fa-volume-up';
    }
}

function updatePlayerUI() {
    if (!state.currentTrack) return;
    
    document.getElementById('player-title').textContent = state.currentTrack.title || 'Unknown';
    document.getElementById('player-artist').textContent = state.currentTrack.artist || 'Unknown Artist';
    
    const albumArt = document.getElementById('player-album-art');
    if (state.currentTrack.cover_art) {
        albumArt.src = `/api/tracks/${state.currentTrack.id}/stream`;
    } else {
        albumArt.src = '';
    }
}

function updatePlayButton() {
    const btn = document.getElementById('play-pause-btn');
    const icon = btn.querySelector('i');
    icon.className = state.isPlaying ? 'fas fa-pause' : 'fas fa-play';
}

function updateProgress() {
    const audio = document.getElementById('audio-player');
    
    if (audio.duration) {
        const percent = (audio.currentTime / audio.duration) * 100;
        document.getElementById('progress').style.width = `${percent}%`;
        document.getElementById('seek-bar').value = percent;
        
        document.getElementById('current-time').textContent = formatDuration(audio.currentTime);
        document.getElementById('duration-time').textContent = formatDuration(audio.duration);
    }
}

function onTrackEnded() {
    playNext();
}

function onTrackLoaded() {
    const audio = document.getElementById('audio-player');
    document.getElementById('duration-time').textContent = formatDuration(audio.duration);
}

// Utility Functions
function formatDuration(seconds) {
    if (!seconds || isNaN(seconds)) return '0:00';
    
    const mins = Math.floor(seconds / 60);
    const secs = Math.floor(seconds % 60);
    return `${mins}:${secs.toString().padStart(2, '0')}`;
}

function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}
