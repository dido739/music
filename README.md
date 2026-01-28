# Music Server 🎵

A comprehensive Python-based web music server application with a beautiful, modern UI for managing and playing your music collection.

![Music Server](https://img.shields.io/badge/Python-3.10+-blue.svg)
![Flask](https://img.shields.io/badge/Flask-3.0-green.svg)
![License](https://img.shields.io/badge/License-MIT-yellow.svg)

## Features

### 🎵 Music Management
- **Automatic Library Scanning**: Scans directories for music files (MP3, FLAC, WAV, OGG, M4A, etc.)
- **Metadata Extraction**: Automatically extracts artist, album, title, duration, and cover art
- **Smart Search**: Real-time search across all tracks with filters
- **Playlist Management**: Create, edit, and manage custom playlists
- **Favorites**: Mark your favorite tracks for quick access

### 🎧 Beautiful Music Player
- **Modern UI**: Clean, responsive design that works on desktop, tablet, and mobile
- **Dark/Light Themes**: Switch between dark and light themes
- **Full Playback Controls**: Play, pause, next, previous, shuffle, and repeat
- **Progress Bar**: Seek to any position in the track
- **Volume Control**: Adjust volume with a slider
- **Now Playing**: View current track with album art

### ⬇️ Download Functionality
- **YouTube Downloader**: Download audio from YouTube videos and playlists
  - Multiple format support (MP3, M4A, OPUS)
  - Quality selection (128-320 kbps)
  - Progress tracking
- **Spotify Downloader**: Download tracks from Spotify
  - Automatic metadata tagging
  - High-quality audio

### ⚙️ Configuration
- **Configurable Directories**: Add/remove music scan directories via UI
- **YAML Configuration**: Simple configuration file
- **Auto-scanning**: Watch for file system changes

## Installation

### Prerequisites
- Python 3.10 or higher
- pip (Python package manager)
- ffmpeg (for audio conversion)

### Install ffmpeg

**Ubuntu/Debian:**
```bash
sudo apt update
sudo apt install ffmpeg
```

**macOS:**
```bash
brew install ffmpeg
```

**Windows:**
Download from [ffmpeg.org](https://ffmpeg.org/download.html)

### Setup

1. **Clone the repository:**
```bash
git clone https://github.com/dido739/music.git
cd music
```

2. **Install Python dependencies:**
```bash
pip install -r requirements.txt
```

3. **Configure the server:**
Edit `config.yaml` to set your music directories and preferences:

```yaml
server:
  host: 0.0.0.0
  port: 5000
  debug: false
  
music_directories:
  - /path/to/your/music/folder1
  - /path/to/your/music/folder2

downloads:
  directory: ./downloads
  youtube:
    enabled: true
    default_format: mp3
    default_quality: 320
  spotify:
    enabled: true
    
database:
  path: ./music_server.db
  
ui:
  theme: dark
  items_per_page: 50
```

4. **Run the server:**
```bash
python app.py
```

5. **Open your browser:**
Navigate to `http://localhost:5000`

## Usage

### Scanning Your Music Library

1. Click the "Scan Library" button in the Library page
2. Wait for the scan to complete
3. Your music will appear in the library grid

### Playing Music

1. Click on any track to play it
2. Use the player controls at the bottom to control playback
3. Click the heart icon to mark tracks as favorites

### Creating Playlists

1. Go to the Playlists page
2. Click "Create Playlist"
3. Enter a name and description
4. Add tracks to your playlist

### Downloading Music

**YouTube:**
1. Go to the Downloads page
2. Paste a YouTube URL
3. Select format and quality
4. Click Download

**Spotify:**
1. Go to the Downloads page
2. Paste a Spotify URL
3. Click Download

### Managing Directories

1. Go to Settings
2. Enter a directory path
3. Click "Add Directory"
4. The directory will be scanned automatically

## API Documentation

The server provides a RESTful API for all operations:

### Tracks
- `GET /api/tracks` - Get all tracks with pagination and filtering
- `GET /api/tracks/:id` - Get a specific track
- `POST /api/tracks/:id/play` - Mark track as played
- `POST /api/tracks/:id/favorite` - Toggle favorite status
- `GET /api/tracks/:id/stream` - Stream a track

### Playlists
- `GET /api/playlists` - Get all playlists
- `POST /api/playlists` - Create a new playlist
- `GET /api/playlists/:id` - Get playlist with tracks
- `PUT /api/playlists/:id` - Update playlist
- `DELETE /api/playlists/:id` - Delete playlist
- `POST /api/playlists/:id/tracks` - Add track to playlist
- `DELETE /api/playlists/:id/tracks/:trackId` - Remove track from playlist

### Scanner
- `POST /api/scan/start` - Start scanning directories
- `GET /api/scan/progress` - Get scan progress

### Downloads
- `POST /api/download/youtube` - Download from YouTube
- `POST /api/download/spotify` - Download from Spotify
- `GET /api/downloads` - Get all downloads

### Configuration
- `GET /api/config` - Get configuration
- `POST /api/config/directories` - Add a music directory
- `DELETE /api/config/directories` - Remove a music directory

### Search & Stats
- `GET /api/search?q=query` - Search tracks
- `GET /api/stats` - Get library statistics

## Project Structure

```
music-server/
├── backend/
│   ├── api/
│   │   ├── __init__.py
│   │   └── routes.py          # API endpoints
│   ├── scanner/
│   │   ├── __init__.py
│   │   └── scanner.py         # Music file scanner
│   ├── downloader/
│   │   ├── __init__.py
│   │   ├── youtube_downloader.py
│   │   └── spotify_downloader.py
│   ├── database/
│   │   ├── __init__.py
│   │   ├── models.py          # Database models
│   │   └── database.py        # Database initialization
│   └── utils/
├── frontend/
│   └── public/
│       ├── index.html         # Main HTML
│       ├── styles.css         # Styles
│       └── app.js             # Frontend JavaScript
├── config.yaml                # Configuration file
├── requirements.txt           # Python dependencies
├── app.py                     # Main application
└── README.md
```

## Technical Stack

**Backend:**
- Python 3.10+
- Flask (Web framework)
- SQLAlchemy (Database ORM)
- Mutagen (Music metadata)
- yt-dlp (YouTube downloads)
- spotdl (Spotify downloads)
- Flask-SocketIO (WebSocket support)

**Frontend:**
- HTML5/CSS3/JavaScript
- Font Awesome (Icons)
- Native HTML5 Audio API

**Database:**
- SQLite

## Configuration Options

### Server Configuration
- `host`: Server host (default: 0.0.0.0)
- `port`: Server port (default: 5000)
- `debug`: Debug mode (default: false)

### Music Directories
- List of directories to scan for music files

### Downloads
- `directory`: Download directory path
- `youtube.enabled`: Enable YouTube downloads
- `youtube.default_format`: Default audio format (mp3, m4a, opus)
- `youtube.default_quality`: Default bitrate (128, 192, 256, 320)
- `spotify.enabled`: Enable Spotify downloads

### Database
- `path`: Database file path

### UI
- `theme`: Default theme (dark, light)
- `items_per_page`: Items per page for pagination

## Keyboard Shortcuts

- `Space` - Play/Pause
- `→` - Next track
- `←` - Previous track
- `↑` - Volume up
- `↓` - Volume down
- `M` - Mute/Unmute

## Troubleshooting

### Music files not appearing
- Make sure the directory path is correct
- Check that files are in supported formats (MP3, FLAC, WAV, OGG, M4A)
- Click "Scan Library" to manually trigger a scan

### Downloads failing
- Ensure ffmpeg is installed and in PATH
- Check internet connection
- Verify the URL is correct

### Player not working
- Check browser console for errors
- Ensure the browser supports HTML5 audio
- Try a different browser

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments

- [Flask](https://flask.palletsprojects.com/) - Web framework
- [yt-dlp](https://github.com/yt-dlp/yt-dlp) - YouTube downloader
- [spotdl](https://github.com/spotDL/spotify-downloader) - Spotify downloader
- [Mutagen](https://github.com/quodlibet/mutagen) - Audio metadata library
- [Font Awesome](https://fontawesome.com/) - Icons

## Support

For issues, questions, or suggestions, please open an issue on GitHub.

---

Made with ❤️ by the Music Server team
