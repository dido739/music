from flask import Blueprint, jsonify, request, send_file, send_from_directory, g
from backend.database.models import Track, Playlist, PlaylistTrack, Settings
from sqlalchemy import or_, func
import os
import logging

logger = logging.getLogger(__name__)

api = Blueprint('api', __name__)

def init_api(app, get_session, scanner, youtube_dl, spotify_dl, config):
    """Initialize API with dependencies"""
    api.get_session = get_session
    api.scanner = scanner
    api.youtube_dl = youtube_dl
    api.spotify_dl = spotify_dl
    api.config = config
    
    app.register_blueprint(api, url_prefix='/api')

def get_db():
    """Helper to get current db session"""
    return g.db_session

# Library endpoints
@api.route('/tracks', methods=['GET'])
def get_tracks():
    """Get all tracks with optional filtering and pagination"""
    try:
        db_session = get_db()
        db_session = get_db()
        page = int(request.args.get('page', 1))
        per_page = int(request.args.get('per_page', 50))
        search = request.args.get('search', '')
        artist = request.args.get('artist', '')
        album = request.args.get('album', '')
        genre = request.args.get('genre', '')
        sort_by = request.args.get('sort_by', 'title')
        sort_order = request.args.get('sort_order', 'asc')
        
        # Build query
        query = db_session.query(Track)
        
        # Apply filters
        if search:
            query = query.filter(
                or_(
                    Track.title.ilike(f'%{search}%'),
                    Track.artist.ilike(f'%{search}%'),
                    Track.album.ilike(f'%{search}%')
                )
            )
        
        if artist:
            query = query.filter(Track.artist.ilike(f'%{artist}%'))
        
        if album:
            query = query.filter(Track.album.ilike(f'%{album}%'))
        
        if genre:
            query = query.filter(Track.genre.ilike(f'%{genre}%'))
        
        # Apply sorting
        if hasattr(Track, sort_by):
            sort_column = getattr(Track, sort_by)
            if sort_order == 'desc':
                query = query.order_by(sort_column.desc())
            else:
                query = query.order_by(sort_column.asc())
        
        # Get total count
        total = query.count()
        
        # Apply pagination
        tracks = query.offset((page - 1) * per_page).limit(per_page).all()
        
        return jsonify({
            'tracks': [track.to_dict() for track in tracks],
            'total': total,
            'page': page,
            'per_page': per_page,
            'pages': (total + per_page - 1) // per_page
        })
    
    except Exception as e:
        logger.error(f"Error getting tracks: {str(e)}")
        return jsonify({'error': str(e)}), 500

@api.route('/tracks/<int:track_id>', methods=['GET'])
def get_track(track_id):
    """Get a specific track"""
    try:
        db_session = get_db()
        track = db_session.query(Track).get(track_id)
        if not track:
            return jsonify({'error': 'Track not found'}), 404
        
        return jsonify(track.to_dict())
    
    except Exception as e:
        logger.error(f"Error getting track: {str(e)}")
        return jsonify({'error': str(e)}), 500

@api.route('/tracks/<int:track_id>/play', methods=['POST'])
def play_track(track_id):
    """Mark track as played"""
    try:
        db_session = get_db()
        from datetime import datetime
        
        track = db_session.query(Track).get(track_id)
        if not track:
            return jsonify({'error': 'Track not found'}), 404
        
        track.play_count = (track.play_count or 0) + 1
        track.last_played = datetime.utcnow()
        db_session.commit()
        
        return jsonify(track.to_dict())
    
    except Exception as e:
        logger.error(f"Error updating play count: {str(e)}")
        db_session.rollback()
        return jsonify({'error': str(e)}), 500

@api.route('/tracks/<int:track_id>/favorite', methods=['POST'])
def toggle_favorite(track_id):
    """Toggle track favorite status"""
    try:
        db_session = get_db()
        track = db_session.query(Track).get(track_id)
        if not track:
            return jsonify({'error': 'Track not found'}), 404
        
        track.favorite = not track.favorite
        db_session.commit()
        
        return jsonify(track.to_dict())
    
    except Exception as e:
        logger.error(f"Error toggling favorite: {str(e)}")
        db_session.rollback()
        return jsonify({'error': str(e)}), 500

@api.route('/tracks/<int:track_id>/stream', methods=['GET'])
def stream_track(track_id):
    """Stream a track"""
    try:
        db_session = get_db()
        track = db_session.query(Track).get(track_id)
        if not track:
            return jsonify({'error': 'Track not found'}), 404
        
        if not os.path.exists(track.path):
            return jsonify({'error': 'File not found'}), 404
        
        return send_file(track.path)
    
    except Exception as e:
        logger.error(f"Error streaming track: {str(e)}")
        return jsonify({'error': str(e)}), 500

# Playlist endpoints
@api.route('/playlists', methods=['GET'])
def get_playlists():
    """Get all playlists"""
    try:
        db_session = get_db()
        playlists = db_session.query(Playlist).all()
        return jsonify([playlist.to_dict() for playlist in playlists])
    
    except Exception as e:
        logger.error(f"Error getting playlists: {str(e)}")
        return jsonify({'error': str(e)}), 500

@api.route('/playlists', methods=['POST'])
def create_playlist():
    """Create a new playlist"""
    try:
        db_session = get_db()
        data = request.get_json()
        
        playlist = Playlist(
            name=data.get('name', 'New Playlist'),
            description=data.get('description', '')
        )
        
        db_session.add(playlist)
        db_session.commit()
        
        return jsonify(playlist.to_dict()), 201
    
    except Exception as e:
        logger.error(f"Error creating playlist: {str(e)}")
        db_session.rollback()
        return jsonify({'error': str(e)}), 500

@api.route('/playlists/<int:playlist_id>', methods=['GET'])
def get_playlist(playlist_id):
    """Get a specific playlist with tracks"""
    try:
        db_session = get_db()
        playlist = db_session.query(Playlist).get(playlist_id)
        if not playlist:
            return jsonify({'error': 'Playlist not found'}), 404
        
        playlist_dict = playlist.to_dict()
        playlist_dict['tracks'] = [
            {
                'position': pt.position,
                'track': pt.track.to_dict()
            }
            for pt in playlist.playlist_tracks
        ]
        
        return jsonify(playlist_dict)
    
    except Exception as e:
        logger.error(f"Error getting playlist: {str(e)}")
        return jsonify({'error': str(e)}), 500

@api.route('/playlists/<int:playlist_id>', methods=['PUT'])
def update_playlist(playlist_id):
    """Update a playlist"""
    try:
        db_session = get_db()
        playlist = db_session.query(Playlist).get(playlist_id)
        if not playlist:
            return jsonify({'error': 'Playlist not found'}), 404
        
        data = request.get_json()
        
        if 'name' in data:
            playlist.name = data['name']
        if 'description' in data:
            playlist.description = data['description']
        
        db_session.commit()
        
        return jsonify(playlist.to_dict())
    
    except Exception as e:
        logger.error(f"Error updating playlist: {str(e)}")
        db_session.rollback()
        return jsonify({'error': str(e)}), 500

@api.route('/playlists/<int:playlist_id>', methods=['DELETE'])
def delete_playlist(playlist_id):
    """Delete a playlist"""
    try:
        db_session = get_db()
        playlist = db_session.query(Playlist).get(playlist_id)
        if not playlist:
            return jsonify({'error': 'Playlist not found'}), 404
        
        db_session.delete(playlist)
        db_session.commit()
        
        return '', 204
    
    except Exception as e:
        logger.error(f"Error deleting playlist: {str(e)}")
        db_session.rollback()
        return jsonify({'error': str(e)}), 500

@api.route('/playlists/<int:playlist_id>/tracks', methods=['POST'])
def add_track_to_playlist(playlist_id):
    """Add a track to playlist"""
    try:
        db_session = get_db()
        playlist = db_session.query(Playlist).get(playlist_id)
        if not playlist:
            return jsonify({'error': 'Playlist not found'}), 404
        
        data = request.get_json()
        track_id = data.get('track_id')
        
        track = db_session.query(Track).get(track_id)
        if not track:
            return jsonify({'error': 'Track not found'}), 404
        
        # Get next position
        max_position = db_session.query(func.max(PlaylistTrack.position)).filter_by(playlist_id=playlist_id).scalar() or 0
        
        playlist_track = PlaylistTrack(
            playlist_id=playlist_id,
            track_id=track_id,
            position=max_position + 1
        )
        
        db_session.add(playlist_track)
        db_session.commit()
        
        return jsonify({'success': True}), 201
    
    except Exception as e:
        logger.error(f"Error adding track to playlist: {str(e)}")
        db_session.rollback()
        return jsonify({'error': str(e)}), 500

@api.route('/playlists/<int:playlist_id>/tracks/<int:track_id>', methods=['DELETE'])
def remove_track_from_playlist(playlist_id, track_id):
    """Remove a track from playlist"""
    try:
        db_session = get_db()
        playlist_track = db_session.query(PlaylistTrack).filter_by(
            playlist_id=playlist_id,
            track_id=track_id
        ).first()
        
        if not playlist_track:
            return jsonify({'error': 'Track not in playlist'}), 404
        
        db_session.delete(playlist_track)
        db_session.commit()
        
        return '', 204
    
    except Exception as e:
        logger.error(f"Error removing track from playlist: {str(e)}")
        db_session.rollback()
        return jsonify({'error': str(e)}), 500

# Scanner endpoints
@api.route('/scan/start', methods=['POST'])
def start_scan():
    """Start scanning music directories"""
    try:
        db_session = get_db()
        data = request.get_json() or {}
        directory = data.get('directory')
        
        # Get directories to scan
        if directory:
            directories = [directory]
        else:
            directories = api.config.get('music_directories', [])
        
        # Start scan in background
        def scan_callback(progress):
            # This would be sent via WebSocket in a full implementation
            pass
        
        import threading
        
        def scan_thread():
            for dir_path in directories:
                api.scanner.scan_directory(dir_path, scan_callback)
        
        thread = threading.Thread(target=scan_thread)
        thread.daemon = True
        thread.start()
        
        return jsonify({'success': True, 'message': 'Scan started'})
    
    except Exception as e:
        logger.error(f"Error starting scan: {str(e)}")
        return jsonify({'error': str(e)}), 500

@api.route('/scan/progress', methods=['GET'])
def get_scan_progress():
    """Get scan progress"""
    try:
        db_session = get_db()
        return jsonify(api.scanner.get_progress())
    
    except Exception as e:
        logger.error(f"Error getting scan progress: {str(e)}")
        return jsonify({'error': str(e)}), 500

# Download endpoints
@api.route('/download/youtube', methods=['POST'])
def download_youtube():
    """Download from YouTube"""
    try:
        db_session = get_db()
        data = request.get_json()
        url = data.get('url')
        
        if not url:
            return jsonify({'error': 'URL required'}), 400
        
        format = data.get('format', 'mp3')
        quality = data.get('quality', 320)
        
        # Start download
        download_id = api.youtube_dl.download_async(url, format=format, quality=quality)
        
        return jsonify({
            'success': True,
            'download_id': download_id
        })
    
    except Exception as e:
        logger.error(f"Error starting YouTube download: {str(e)}")
        return jsonify({'error': str(e)}), 500

@api.route('/download/spotify', methods=['POST'])
def download_spotify():
    """Download from Spotify"""
    try:
        db_session = get_db()
        data = request.get_json()
        url = data.get('url')
        
        if not url:
            return jsonify({'error': 'URL required'}), 400
        
        # Start download
        download_id = api.spotify_dl.download_async(url)
        
        return jsonify({
            'success': True,
            'download_id': download_id
        })
    
    except Exception as e:
        logger.error(f"Error starting Spotify download: {str(e)}")
        return jsonify({'error': str(e)}), 500

@api.route('/downloads', methods=['GET'])
def get_downloads():
    """Get all downloads"""
    try:
        db_session = get_db()
        youtube_downloads = api.youtube_dl.get_all_downloads()
        spotify_downloads = api.spotify_dl.get_all_downloads()
        
        return jsonify({
            'youtube': youtube_downloads,
            'spotify': spotify_downloads
        })
    
    except Exception as e:
        logger.error(f"Error getting downloads: {str(e)}")
        return jsonify({'error': str(e)}), 500

# Config endpoints
@api.route('/config', methods=['GET'])
def get_config():
    """Get configuration"""
    try:
        db_session = get_db()
        return jsonify(api.config)
    
    except Exception as e:
        logger.error(f"Error getting config: {str(e)}")
        return jsonify({'error': str(e)}), 500

@api.route('/config/directories', methods=['POST'])
def add_directory():
    """Add a music directory"""
    try:
        db_session = get_db()
        data = request.get_json()
        directory = data.get('directory')
        
        if not directory:
            return jsonify({'error': 'Directory required'}), 400
        
        if 'music_directories' not in api.config:
            api.config['music_directories'] = []
        
        if directory not in api.config['music_directories']:
            api.config['music_directories'].append(directory)
            
            # Save config
            import yaml
            with open('config.yaml', 'w') as f:
                yaml.dump(api.config, f)
        
        return jsonify({'success': True})
    
    except Exception as e:
        logger.error(f"Error adding directory: {str(e)}")
        return jsonify({'error': str(e)}), 500

@api.route('/config/directories', methods=['DELETE'])
def remove_directory():
    """Remove a music directory"""
    try:
        db_session = get_db()
        data = request.get_json()
        directory = data.get('directory')
        
        if not directory:
            return jsonify({'error': 'Directory required'}), 400
        
        if 'music_directories' in api.config and directory in api.config['music_directories']:
            api.config['music_directories'].remove(directory)
            
            # Save config
            import yaml
            with open('config.yaml', 'w') as f:
                yaml.dump(api.config, f)
        
        return jsonify({'success': True})
    
    except Exception as e:
        logger.error(f"Error removing directory: {str(e)}")
        return jsonify({'error': str(e)}), 500

# Search endpoint
@api.route('/search', methods=['GET'])
def search():
    """Search across all fields"""
    try:
        db_session = get_db()
        query_str = request.args.get('q', '')
        
        if not query_str:
            return jsonify({'tracks': []})
        
        tracks = db_session.query(Track).filter(
            or_(
                Track.title.ilike(f'%{query_str}%'),
                Track.artist.ilike(f'%{query_str}%'),
                Track.album.ilike(f'%{query_str}%'),
                Track.genre.ilike(f'%{query_str}%')
            )
        ).limit(50).all()
        
        return jsonify({
            'tracks': [track.to_dict() for track in tracks]
        })
    
    except Exception as e:
        logger.error(f"Error searching: {str(e)}")
        return jsonify({'error': str(e)}), 500

# Stats endpoint
@api.route('/stats', methods=['GET'])
def get_stats():
    """Get library statistics"""
    try:
        db_session = get_db()
        total_tracks = db_session.query(Track).count()
        total_artists = db_session.query(Track.artist).distinct().count()
        total_albums = db_session.query(Track.album).distinct().count()
        total_playlists = db_session.query(Playlist).count()
        
        # Get total duration
        total_duration = db_session.query(func.sum(Track.duration)).scalar() or 0
        
        return jsonify({
            'total_tracks': total_tracks,
            'total_artists': total_artists,
            'total_albums': total_albums,
            'total_playlists': total_playlists,
            'total_duration': total_duration
        })
    
    except Exception as e:
        logger.error(f"Error getting stats: {str(e)}")
        return jsonify({'error': str(e)}), 500
