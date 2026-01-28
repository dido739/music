import os
import logging
from mutagen import File as MutagenFile
from mutagen.id3 import ID3, APIC
from mutagen.flac import FLAC, Picture
from mutagen.mp4 import MP4, MP4Cover
from pathlib import Path
import hashlib
import base64
from datetime import datetime

logger = logging.getLogger(__name__)

class MusicScanner:
    SUPPORTED_FORMATS = {'.mp3', '.flac', '.wav', '.ogg', '.m4a', '.opus', '.wma', '.aac'}
    
    def __init__(self, db_session, cover_art_dir='./covers'):
        self.db_session = db_session
        self.cover_art_dir = cover_art_dir
        self.scan_progress = {
            'total': 0,
            'scanned': 0,
            'added': 0,
            'updated': 0,
            'errors': 0,
            'current_file': ''
        }
        
        # Create cover art directory
        os.makedirs(cover_art_dir, exist_ok=True)
    
    def scan_directory(self, directory, progress_callback=None):
        """Scan a directory for music files"""
        from backend.database.models import Track
        
        logger.info(f"Scanning directory: {directory}")
        
        if not os.path.exists(directory):
            logger.error(f"Directory does not exist: {directory}")
            return self.scan_progress
        
        # Find all music files
        music_files = []
        for root, dirs, files in os.walk(directory):
            for file in files:
                if Path(file).suffix.lower() in self.SUPPORTED_FORMATS:
                    music_files.append(os.path.join(root, file))
        
        self.scan_progress['total'] = len(music_files)
        logger.info(f"Found {len(music_files)} music files")
        
        # Process each file
        for file_path in music_files:
            self.scan_progress['current_file'] = file_path
            
            try:
                # Check if file already exists in database
                existing_track = self.db_session.query(Track).filter_by(path=file_path).first()
                
                # Extract metadata
                metadata = self.extract_metadata(file_path)
                
                if existing_track:
                    # Update existing track
                    for key, value in metadata.items():
                        setattr(existing_track, key, value)
                    self.scan_progress['updated'] += 1
                else:
                    # Add new track
                    new_track = Track(**metadata)
                    self.db_session.add(new_track)
                    self.scan_progress['added'] += 1
                
                self.db_session.commit()
                
            except Exception as e:
                logger.error(f"Error processing {file_path}: {str(e)}")
                self.scan_progress['errors'] += 1
                self.db_session.rollback()
            
            self.scan_progress['scanned'] += 1
            
            # Call progress callback if provided
            if progress_callback:
                progress_callback(self.scan_progress)
        
        logger.info(f"Scan complete. Added: {self.scan_progress['added']}, "
                   f"Updated: {self.scan_progress['updated']}, "
                   f"Errors: {self.scan_progress['errors']}")
        
        return self.scan_progress
    
    def extract_metadata(self, file_path):
        """Extract metadata from a music file"""
        metadata = {
            'path': file_path,
            'title': None,
            'artist': None,
            'album': None,
            'genre': None,
            'year': None,
            'duration': None,
            'track_number': None,
            'disc_number': None,
            'bitrate': None,
            'sample_rate': None,
            'file_size': None,
            'format': None,
            'cover_art': None
        }
        
        try:
            # Get file size
            metadata['file_size'] = os.path.getsize(file_path)
            
            # Get format
            metadata['format'] = Path(file_path).suffix[1:].upper()
            
            # Extract audio metadata using mutagen
            audio = MutagenFile(file_path, easy=False)
            
            if audio is None:
                logger.warning(f"Could not read metadata from {file_path}")
                metadata['title'] = Path(file_path).stem
                return metadata
            
            # Get duration
            if hasattr(audio.info, 'length'):
                metadata['duration'] = audio.info.length
            
            # Get bitrate
            if hasattr(audio.info, 'bitrate'):
                metadata['bitrate'] = audio.info.bitrate
            
            # Get sample rate
            if hasattr(audio.info, 'sample_rate'):
                metadata['sample_rate'] = audio.info.sample_rate
            
            # Extract tags based on file type
            if hasattr(audio, 'tags') and audio.tags:
                metadata.update(self._extract_tags(audio, file_path))
            else:
                metadata['title'] = Path(file_path).stem
            
            # Extract cover art
            cover_art_path = self._extract_cover_art(audio, file_path)
            if cover_art_path:
                metadata['cover_art'] = cover_art_path
            
        except Exception as e:
            logger.error(f"Error extracting metadata from {file_path}: {str(e)}")
            metadata['title'] = Path(file_path).stem
        
        return metadata
    
    def _extract_tags(self, audio, file_path):
        """Extract tags from audio file"""
        tags = {}
        
        try:
            if hasattr(audio, 'tags'):
                audio_tags = audio.tags
                
                # Common tag mappings
                tag_map = {
                    'title': ['TIT2', 'title', '\xa9nam'],
                    'artist': ['TPE1', 'artist', '\xa9ART'],
                    'album': ['TALB', 'album', '\xa9alb'],
                    'genre': ['TCON', 'genre', '\xa9gen'],
                    'year': ['TDRC', 'date', '\xa9day'],
                    'track_number': ['TRCK', 'tracknumber', 'trkn'],
                    'disc_number': ['TPOS', 'discnumber', 'disk']
                }
                
                for field, tag_keys in tag_map.items():
                    for tag_key in tag_keys:
                        try:
                            if tag_key in audio_tags:
                                value = audio_tags[tag_key]
                                
                                # Handle different value types
                                if isinstance(value, list) and len(value) > 0:
                                    value = value[0]
                                
                                # Convert to string and clean up
                                if hasattr(value, 'text'):
                                    value = str(value.text[0]) if value.text else None
                                else:
                                    value = str(value)
                                
                                # Special handling for year
                                if field == 'year' and value:
                                    try:
                                        tags['year'] = int(str(value)[:4])
                                    except:
                                        pass
                                # Special handling for track/disc number
                                elif field in ['track_number', 'disc_number'] and value:
                                    try:
                                        # Handle "1/10" format
                                        if '/' in str(value):
                                            value = str(value).split('/')[0]
                                        tags[field] = int(value)
                                    except:
                                        pass
                                elif value:
                                    tags[field] = value
                                
                                break
                        except Exception as e:
                            logger.debug(f"Error extracting tag {tag_key}: {str(e)}")
                            continue
        except Exception as e:
            logger.error(f"Error extracting tags: {str(e)}")
        
        # Default to filename if no title
        if 'title' not in tags or not tags['title']:
            tags['title'] = Path(file_path).stem
        
        return tags
    
    def _extract_cover_art(self, audio, file_path):
        """Extract cover art from audio file"""
        try:
            cover_data = None
            
            # MP3 files
            if hasattr(audio, 'tags') and isinstance(audio.tags, type(ID3())):
                for tag in audio.tags.values():
                    if isinstance(tag, APIC):
                        cover_data = tag.data
                        break
            
            # FLAC files
            elif isinstance(audio, FLAC):
                if audio.pictures:
                    cover_data = audio.pictures[0].data
            
            # MP4/M4A files
            elif isinstance(audio, MP4):
                if 'covr' in audio.tags:
                    cover_data = bytes(audio.tags['covr'][0])
            
            # Save cover art if found
            if cover_data:
                # Generate unique filename based on file path hash
                file_hash = hashlib.md5(file_path.encode()).hexdigest()
                cover_filename = f"{file_hash}.jpg"
                cover_path = os.path.join(self.cover_art_dir, cover_filename)
                
                with open(cover_path, 'wb') as f:
                    f.write(cover_data)
                
                return cover_path
        
        except Exception as e:
            logger.debug(f"Could not extract cover art: {str(e)}")
        
        return None
    
    def get_progress(self):
        """Get current scan progress"""
        return self.scan_progress
    
    def reset_progress(self):
        """Reset scan progress"""
        self.scan_progress = {
            'total': 0,
            'scanned': 0,
            'added': 0,
            'updated': 0,
            'errors': 0,
            'current_file': ''
        }
