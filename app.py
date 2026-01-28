#!/usr/bin/env python3
"""
Music Server - A comprehensive web-based music server application
"""

from flask import Flask, send_from_directory
from flask_cors import CORS
import yaml
import logging
import os
import sys

# Add backend to path
sys.path.insert(0, os.path.dirname(__file__))

from backend.database.database import init_db
from backend.scanner import MusicScanner
from backend.downloader import YouTubeDownloader, SpotifyDownloader
from backend.api.routes import init_api

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Load configuration
def load_config(config_file='config.yaml'):
    """Load configuration from YAML file"""
    try:
        with open(config_file, 'r') as f:
            return yaml.safe_load(f)
    except FileNotFoundError:
        logger.warning(f"Config file {config_file} not found, using defaults")
        return {
            'server': {'host': '0.0.0.0', 'port': 5000, 'debug': False},
            'music_directories': ['./music'],
            'downloads': {
                'directory': './downloads',
                'youtube': {'enabled': True, 'default_format': 'mp3', 'default_quality': 320},
                'spotify': {'enabled': True}
            },
            'database': {'path': './music_server.db'},
            'ui': {'theme': 'dark', 'items_per_page': 50}
        }

def create_app(config=None):
    """Create and configure the Flask app"""
    app = Flask(__name__, static_folder='frontend/public', static_url_path='')
    
    # Load config
    if config is None:
        config = load_config()
    
    # Enable CORS
    CORS(app)
    
    # Initialize database
    db_path = config.get('database', {}).get('path', './music_server.db')
    Session = init_db(db_path)
    
    logger.info(f"Database initialized at {db_path}")
    
    # Create a function to get db session per request
    @app.before_request
    def before_request():
        from flask import g
        g.db_session = Session()
    
    @app.teardown_appcontext
    def shutdown_session(exception=None):
        from flask import g
        db_session = g.pop('db_session', None)
        if db_session is not None:
            db_session.close()
    
    # Get session from flask g
    from flask import g
    def get_session():
        return g.db_session
    
    # Initialize scanner
    scanner = MusicScanner(None)  # We'll pass session in routes
    logger.info("Music scanner initialized")
    
    # Initialize downloaders
    download_dir = config.get('downloads', {}).get('directory', './downloads')
    youtube_config = config.get('downloads', {}).get('youtube', {})
    
    youtube_dl = YouTubeDownloader(
        download_dir=download_dir,
        default_format=youtube_config.get('default_format', 'mp3'),
        default_quality=youtube_config.get('default_quality', 320),
        cookiefile=youtube_config.get('cookiefile')
    )
    
    spotify_dl = SpotifyDownloader(download_dir=download_dir)
    
    logger.info("Downloaders initialized")
    
    # Store session factory
    app.Session = Session
    
    # Initialize API
    init_api(app, get_session, scanner, youtube_dl, spotify_dl, config)
    logger.info("API initialized")
    
    # Serve frontend
    @app.route('/')
    def index():
        return send_from_directory(app.static_folder, 'index.html')
    
    @app.route('/<path:path>')
    def static_files(path):
        return send_from_directory(app.static_folder, path)
    
    return app

def main():
    """Main entry point"""
    # Load config
    config = load_config()
    
    # Create app
    app = create_app(config)
    
    # Get server config
    server_config = config.get('server', {})
    host = server_config.get('host', '0.0.0.0')
    port = server_config.get('port', 5000)
    debug = server_config.get('debug', False)
    
    # Create directories
    for directory in config.get('music_directories', []):
        os.makedirs(directory, exist_ok=True)
    
    os.makedirs(config.get('downloads', {}).get('directory', './downloads'), exist_ok=True)
    os.makedirs('./covers', exist_ok=True)
    
    logger.info(f"Starting Music Server on {host}:{port}")
    logger.info(f"Music directories: {config.get('music_directories', [])}")
    logger.info(f"Download directory: {config.get('downloads', {}).get('directory', './downloads')}")
    logger.info(f"Open your browser at http://localhost:{port}")
    
    # Run server
    app.run(host=host, port=port, debug=debug)

if __name__ == '__main__':
    main()
