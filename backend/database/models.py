from sqlalchemy import create_engine, Column, Integer, String, Float, DateTime, ForeignKey, Table, Boolean
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, sessionmaker
from datetime import datetime

Base = declarative_base()

class Track(Base):
    __tablename__ = 'tracks'
    
    id = Column(Integer, primary_key=True)
    path = Column(String, unique=True, nullable=False)
    title = Column(String)
    artist = Column(String)
    album = Column(String)
    genre = Column(String)
    year = Column(Integer)
    duration = Column(Float)
    track_number = Column(Integer)
    disc_number = Column(Integer)
    bitrate = Column(Integer)
    sample_rate = Column(Integer)
    file_size = Column(Integer)
    format = Column(String)
    cover_art = Column(String)  # Path to extracted cover art
    date_added = Column(DateTime, default=datetime.utcnow)
    last_played = Column(DateTime)
    play_count = Column(Integer, default=0)
    favorite = Column(Boolean, default=False)
    
    # Relationships
    playlist_tracks = relationship('PlaylistTrack', back_populates='track', cascade='all, delete-orphan')
    
    def to_dict(self):
        return {
            'id': self.id,
            'path': self.path,
            'title': self.title,
            'artist': self.artist,
            'album': self.album,
            'genre': self.genre,
            'year': self.year,
            'duration': self.duration,
            'track_number': self.track_number,
            'disc_number': self.disc_number,
            'bitrate': self.bitrate,
            'sample_rate': self.sample_rate,
            'file_size': self.file_size,
            'format': self.format,
            'cover_art': self.cover_art,
            'date_added': self.date_added.isoformat() if self.date_added else None,
            'last_played': self.last_played.isoformat() if self.last_played else None,
            'play_count': self.play_count,
            'favorite': self.favorite
        }

class Playlist(Base):
    __tablename__ = 'playlists'
    
    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    description = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    playlist_tracks = relationship('PlaylistTrack', back_populates='playlist', cascade='all, delete-orphan', order_by='PlaylistTrack.position')
    
    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
            'track_count': len(self.playlist_tracks)
        }

class PlaylistTrack(Base):
    __tablename__ = 'playlist_tracks'
    
    id = Column(Integer, primary_key=True)
    playlist_id = Column(Integer, ForeignKey('playlists.id'), nullable=False)
    track_id = Column(Integer, ForeignKey('tracks.id'), nullable=False)
    position = Column(Integer, nullable=False)
    added_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    playlist = relationship('Playlist', back_populates='playlist_tracks')
    track = relationship('Track', back_populates='playlist_tracks')

class Settings(Base):
    __tablename__ = 'settings'
    
    id = Column(Integer, primary_key=True)
    key = Column(String, unique=True, nullable=False)
    value = Column(String)
    
    def to_dict(self):
        return {
            'key': self.key,
            'value': self.value
        }

# Create engine and session
db = None

def get_db():
    return db
