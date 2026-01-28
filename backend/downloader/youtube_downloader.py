import os
import logging
import yt_dlp
from pathlib import Path
import threading
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type

logger = logging.getLogger(__name__)

class YouTubeDownloader:
    def __init__(self, download_dir='./downloads', default_format='mp3', default_quality=320, cookiefile=None):
        self.download_dir = download_dir
        self.default_format = default_format
        self.default_quality = default_quality
        self.cookiefile = cookiefile
        self.downloads = {}  # Track active downloads
        self.download_id = 0
        
        # Create download directory
        os.makedirs(download_dir, exist_ok=True)
    
    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=4, max=10),
        retry=retry_if_exception_type(yt_dlp.utils.DownloadError)
    )
    def _download_with_retry(self, url, ydl_opts):
        """Download with retry logic for transient errors"""
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            return ydl.extract_info(url, download=True)
    
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
        
        # Configure yt-dlp options with enhanced settings to fix 403 errors
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
            
            # Enhanced options to fix 403 errors
            'http_headers': {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36',
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
                'Accept-Language': 'en-us,en;q=0.5',
                'Sec-Fetch-Mode': 'navigate',
            },
            'extractor_args': {
                'youtube': {
                    'player_client': ['android', 'web'],
                    'player_skip': ['webpage', 'configs'],
                }
            },
            'geo_bypass': True,
            'socket_timeout': 30,
        }
        
        # Add cookie file if provided
        if self.cookiefile and os.path.exists(self.cookiefile):
            ydl_opts['cookiefile'] = self.cookiefile
            logger.info(f"Using cookies from: {self.cookiefile}")
        
        try:
            info = self._download_with_retry(url, ydl_opts)
            
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
        
        except yt_dlp.utils.DownloadError as e:
            error_str = str(e)
            logger.error(f"Error downloading {url}: {error_str}")
            
            # Provide specific guidance for 403 errors
            if '403' in error_str or 'Forbidden' in error_str:
                logger.error("HTTP 403 Forbidden - YouTube may be blocking requests.")
                logger.info("Troubleshooting steps:\n"
                           "  1. Update yt-dlp: pip install -U yt-dlp\n"
                           "  2. If issue persists, you may need to provide cookies from your browser.\n"
                           "  3. Export cookies using a browser extension like 'Get cookies.txt'\n"
                           "  4. Configure the cookie file path in config.yaml")
            
            self.downloads[download_id]['status'] = 'error'
            self.downloads[download_id]['error'] = error_str
            
            if progress_callback:
                progress_callback(self.downloads[download_id])
            
            return self.downloads[download_id]
        
        except Exception as e:
            logger.error(f"Unexpected error downloading {url}: {str(e)}")
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
