"""
User-related Pydantic models
"""

from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field, validator
from src.models.base import LastFmImage, LastFmDate


class UserInfo(BaseModel):
    """User profile information"""
    name: str
    realname: str = ""
    url: str = ""
    country: str = ""
    age: Optional[int] = None
    gender: str = ""
    subscriber: bool = False
    playcount: int = 0
    playlists: int = 0
    bootstrap: int = 0
    registered: Optional[LastFmDate] = None
    image: Optional[LastFmImage] = None
    
    @validator('age', 'playcount', 'playlists', 'bootstrap', pre=True)
    def convert_to_int(cls, v):
        """Convert string numbers to integers"""
        if v is None:
            return None
        if isinstance(v, str):
            return int(v) if v.isdigit() else 0
        return v or 0
    
    @validator('subscriber', pre=True)
    def convert_subscriber(cls, v):
        """Convert subscriber to boolean"""
        if isinstance(v, str):
            return v == "1"
        return bool(v)
    
    @classmethod
    def from_lastfm_user(cls, user_data: Dict[str, Any]) -> "UserInfo":
        """Convert Last.fm user data to model"""
        return cls(
            name=user_data.get("name", ""),
            realname=user_data.get("realname", ""),
            url=user_data.get("url", ""),
            country=user_data.get("country", ""),
            age=user_data.get("age"),
            gender=user_data.get("gender", ""),
            subscriber=user_data.get("subscriber", "0") == "1",
            playcount=user_data.get("playcount", 0),
            playlists=user_data.get("playlists", 0),
            bootstrap=user_data.get("bootstrap", 0),
            registered=LastFmDate.from_lastfm_date(user_data.get("registered", {}).get("unixtime") if isinstance(user_data.get("registered"), dict) else user_data.get("registered")),
            image=LastFmImage.from_lastfm_images(user_data.get("image", []))
        )


class Scrobble(BaseModel):
    """Scrobbled track information"""
    track: str
    artist: str
    album: Optional[str] = None
    timestamp: Optional[int] = None
    date: Optional[LastFmDate] = None
    mbid: str = ""
    image: Optional[LastFmImage] = None
    nowplaying: bool = False
    
    @classmethod
    def from_lastfm_scrobble(cls, scrobble_data: Dict[str, Any]) -> "Scrobble":
        """Convert Last.fm recent track to model"""
        # Handle artist field
        artist_data = scrobble_data.get("artist", {})
        if isinstance(artist_data, dict):
            artist_name = artist_data.get("#text", "")
        else:
            artist_name = str(artist_data)
        
        # Handle album field
        album_data = scrobble_data.get("album", {})
        if isinstance(album_data, dict):
            album_name = album_data.get("#text", "")
        else:
            album_name = str(album_data) if album_data else None
        
        # Check if currently playing
        nowplaying = "@attr" in scrobble_data and scrobble_data["@attr"].get("nowplaying") == "true"
        
        return cls(
            track=scrobble_data.get("name", ""),
            artist=artist_name,
            album=album_name,
            mbid=scrobble_data.get("mbid", ""),
            date=LastFmDate.from_lastfm_date(scrobble_data.get("date")),
            image=LastFmImage.from_lastfm_images(scrobble_data.get("image", [])),
            nowplaying=nowplaying
        )


class RecentTracksResponse(BaseModel):
    """User's recent tracks response"""
    user: str = ""
    total: int = 0
    page: int = 1
    per_page: int = 50
    total_pages: int = 1
    tracks: List[Scrobble] = Field(default_factory=list)
