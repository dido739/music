import os
import logging
import subprocess
import threading

logger = logging.getLogger(__name__)

class SpotifyDownloader:
    def __init__(self, download_dir='./downloads'):
        self.download_dir = download_dir
        self.downloads = {}
        self.download_id = 0
        
        # Create download directory
        os.makedirs(download_dir, exist_ok=True)
    
    def download(self, url, progress_callback=None):
        """Download audio from Spotify URL using spotdl"""
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
        
        try:
            # Use spotdl to download
            cmd = [
                'spotdl',
                'download',
                url,
                '--output', self.download_dir,
                '--format', 'mp3',
                '--bitrate', '320k'
            ]
            
            self.downloads[download_id]['status'] = 'downloading'
            
            if progress_callback:
                progress_callback(self.downloads[download_id])
            
            # Run spotdl command
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=600  # 10 minute timeout
            )
            
            if result.returncode == 0:
                self.downloads[download_id]['status'] = 'completed'
                self.downloads[download_id]['progress'] = 100
                
                # Try to find the downloaded file
                # spotdl typically names files as "Artist - Title.mp3"
                # We'll just mark it as completed and let the scanner find it
                
                if progress_callback:
                    progress_callback(self.downloads[download_id])
                
                return self.downloads[download_id]
            else:
                raise Exception(f"spotdl error: {result.stderr}")
        
        except Exception as e:
            logger.error(f"Error downloading {url}: {str(e)}")
            self.downloads[download_id]['status'] = 'error'
            self.downloads[download_id]['error'] = str(e)
            
            if progress_callback:
                progress_callback(self.downloads[download_id])
            
            return self.downloads[download_id]
    
    def download_async(self, url, progress_callback=None):
        """Download audio asynchronously"""
        thread = threading.Thread(
            target=self.download,
            args=(url,),
            kwargs={'progress_callback': progress_callback}
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
