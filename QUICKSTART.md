# Quick Start Guide

This guide will help you get the Music Server up and running in minutes.

## Prerequisites

1. **Python 3.10+**
   ```bash
   python3 --version  # Should be 3.10 or higher
   ```

2. **ffmpeg** (for audio conversion)
   - Ubuntu/Debian: `sudo apt install ffmpeg`
   - macOS: `brew install ffmpeg`
   - Windows: Download from https://ffmpeg.org/download.html

## Installation

1. **Clone the repository:**
   ```bash
   git clone https://github.com/dido739/music.git
   cd music
   ```

2. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Run the server:**
   ```bash
   python app.py
   ```

4. **Open your browser:**
   Navigate to http://localhost:5000

## First Steps

### 1. Add Your Music Directory

1. Go to **Settings** page
2. Enter your music folder path (e.g., `/home/user/Music`)
3. Click **Add Directory**

### 2. Scan Your Library

1. Go to **Library** page
2. Click **Scan Library** button
3. Wait for the scan to complete
4. Your music will appear in the library grid

### 3. Play Music

1. Click on any track to start playing
2. Use the player controls at the bottom:
   - Play/Pause
   - Next/Previous track
   - Shuffle and Repeat
   - Volume control
   - Seek bar

### 4. Create Playlists

1. Go to **Playlists** page
2. Click **Create Playlist**
3. Enter a name and description
4. Add tracks from your library

### 5. Download Music

**YouTube:**
1. Go to **Downloads** page
2. Paste a YouTube URL
3. Select format and quality
4. Click **Download**

**Spotify:**
1. Go to **Downloads** page
2. Paste a Spotify URL
3. Click **Download**

Downloaded files will automatically be added to your library after scanning.

## Configuration

Edit `config.yaml` to customize:

```yaml
server:
  host: 0.0.0.0  # Change to localhost for local-only access
  port: 5000     # Change port if needed

music_directories:
  - /path/to/music  # Add multiple directories

downloads:
  directory: ./downloads
  youtube:
    default_format: mp3  # mp3, m4a, opus
    default_quality: 320 # 128, 192, 256, 320
```

## Troubleshooting

**Music not appearing?**
- Check directory path is correct
- Ensure files are in supported formats (MP3, FLAC, WAV, OGG, M4A)
- Click "Scan Library" manually

**Download not working?**
- Verify ffmpeg is installed: `ffmpeg -version`
- Check internet connection
- Try a different URL

**Server won't start?**
- Check port 5000 is not in use
- Try a different port in config.yaml
- Check Python version is 3.10+

## Tips

- Use **Search** to quickly find tracks
- Mark favorites by clicking the heart icon
- Use **Shuffle** and **Repeat** for continuous playback
- Switch between **Dark** and **Light** themes in Settings
- Access the API at http://localhost:5000/api/

## Need Help?

See the full [README.md](README.md) for detailed documentation and API reference.

For issues, visit: https://github.com/dido739/music/issues
