"""
Track-related Pydantic models
"""

from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field, validator
from src.models.base import LastFmImage


class Track(BaseModel):
    """Track information"""
    name: str
    artist: str
    album: Optional[str] = None
    mbid: str = ""
    url: str = ""
    duration: Optional[int] = None  # in seconds
    playcount: int = 0
    listeners: Optional[int] = None
    image: Optional[LastFmImage] = None
    tags: List[str] = Field(default_factory=list)
    wiki: Optional[str] = None
    
    @validator('playcount', 'listeners', 'duration', pre=True)
    def convert_to_int(cls, v):
        """Convert string numbers to integers"""
        if v is None:
            return None
        if isinstance(v, str):
            return int(v) if v.isdigit() else 0
        return v or 0
    
    @classmethod
    def from_lastfm_track(cls, track_data: Dict[str, Any]) -> "Track":
        """Convert Last.fm track data to model"""
        # Handle artist field (can be string or dict)
        artist_data = track_data.get("artist", "")
        if isinstance(artist_data, dict):
            artist_name = artist_data.get("name", "")
        else:
            artist_name = str(artist_data)
        
        # Handle album field (can be string or dict)
        album_data = track_data.get("album", "")
        if isinstance(album_data, dict):
            album_name = album_data.get("title", "") or album_data.get("name", "")
        else:
            album_name = str(album_data) if album_data else None
        
        # Extract tags
        tags_data = track_data.get("tags", {}).get("tag", [])
        if isinstance(tags_data, dict):  # Single tag
            tags_data = [tags_data]
        tags = [tag.get("name", "") for tag in tags_data if isinstance(tag, dict)]
        
        # Extract wiki
        wiki_data = track_data.get("wiki", {})
        wiki = wiki_data.get("summary", "") if wiki_data else None
        
        return cls(
            name=track_data.get("name", ""),
            artist=artist_name,
            album=album_name,
            mbid=track_data.get("mbid", ""),
            url=track_data.get("url", ""),
            duration=track_data.get("duration"),
            playcount=track_data.get("playcount", 0),
            listeners=track_data.get("listeners"),
            image=LastFmImage.from_lastfm_images(track_data.get("image", [])),
            tags=tags,
            wiki=wiki
        )


class TrackListResponse(BaseModel):
    """Response for track lists (top tracks, etc.)"""
    artist: str = ""
    total: int = 0
    page: int = 1
    per_page: int = 50
    tracks: List[Track] = Field(default_factory=list)


class TrackSearchResult(BaseModel):
    """Single track from search results"""
    name: str
    artist: str
    mbid: str = ""
    url: str = ""
    listeners: int = 0
    image: Optional[LastFmImage] = None
    
    @classmethod
    def from_lastfm_search(cls, search_data: Dict[str, Any]) -> "TrackSearchResult":
        """Convert Last.fm search result to model"""
        return cls(
            name=search_data.get("name", ""),
            artist=search_data.get("artist", ""),
            mbid=search_data.get("mbid", ""),
            url=search_data.get("url", ""),
            listeners=search_data.get("listeners", 0),
            image=LastFmImage.from_lastfm_images(search_data.get("image", []))
        )


class TrackSearchResponse(BaseModel):
    """Track search response with pagination"""
    query: str = ""
    total_results: int = 0
    start_page: int = 1
    items_per_page: int = 30
    tracks: List[TrackSearchResult] = Field(default_factory=list)
