import os
import logging
import yt_dlp
from pathlib import Path
import threading

logger = logging.getLogger(__name__)

class YouTubeDownloader:
    def __init__(self, download_dir='./downloads', default_format='mp3', default_quality=320):
        self.download_dir = download_dir
        self.default_format = default_format
        self.default_quality = default_quality
        self.downloads = {}  # Track active downloads
        self.download_id = 0
        
        # Create download directory
        os.makedirs(download_dir, exist_ok=True)
    
    def download(self, url, format=None, quality=None, progress_callback=None):
        """Download audio from YouTube URL"""
        format = format or self.default_format
        quality = quality or self.default_quality
        
        # Generate download ID
        self.download_id += 1
        download_id = self.download_id
        
        # Initialize download status
        self.downloads[download_id] = {
            'url': url,
            'status': 'starting',
            'progress': 0,
            'filename': None,
            'error': None
        }
        
        def progress_hook(d):
            if d['status'] == 'downloading':
                try:
                    percent = d.get('_percent_str', '0%').strip().rstrip('%')
                    self.downloads[download_id]['progress'] = float(percent)
                    self.downloads[download_id]['status'] = 'downloading'
                    
                    if progress_callback:
                        progress_callback(self.downloads[download_id])
                except:
                    pass
            
            elif d['status'] == 'finished':
                self.downloads[download_id]['status'] = 'processing'
                self.downloads[download_id]['filename'] = d.get('filename')
                
                if progress_callback:
                    progress_callback(self.downloads[download_id])
        
        # Configure yt-dlp options
        ydl_opts = {
            'format': 'bestaudio/best',
            'outtmpl': os.path.join(self.download_dir, '%(title)s.%(ext)s'),
            'progress_hooks': [progress_hook],
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': format,
                'preferredquality': str(quality),
            }],
            'postprocessor_args': [
                '-ar', '44100'
            ],
            'prefer_ffmpeg': True,
            'keepvideo': False,
            'quiet': True,
            'no_warnings': True,
        }
        
        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(url, download=True)
                
                # Update final status
                self.downloads[download_id]['status'] = 'completed'
                self.downloads[download_id]['progress'] = 100
                
                # Get the actual filename
                if info:
                    title = info.get('title', 'download')
                    filename = f"{title}.{format}"
                    self.downloads[download_id]['filename'] = os.path.join(self.download_dir, filename)
                    self.downloads[download_id]['title'] = title
                
                if progress_callback:
                    progress_callback(self.downloads[download_id])
                
                return self.downloads[download_id]
        
        except Exception as e:
            logger.error(f"Error downloading {url}: {str(e)}")
            self.downloads[download_id]['status'] = 'error'
            self.downloads[download_id]['error'] = str(e)
            
            if progress_callback:
                progress_callback(self.downloads[download_id])
            
            return self.downloads[download_id]
    
    def download_async(self, url, format=None, quality=None, progress_callback=None):
        """Download audio asynchronously"""
        thread = threading.Thread(
            target=self.download,
            args=(url,),
            kwargs={'format': format, 'quality': quality, 'progress_callback': progress_callback}
        )
        thread.daemon = True
        thread.start()
        
        return self.download_id
    
    def get_download_status(self, download_id):
        """Get status of a download"""
        return self.downloads.get(download_id)
    
    def get_all_downloads(self):
        """Get all download statuses"""
        return self.downloads
