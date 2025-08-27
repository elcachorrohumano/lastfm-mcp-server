"""
Chart-related Pydantic models
"""

from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field, validator
from src.models.base import LastFmImage


class ChartArtist(BaseModel):
    """Artist from charts"""
    name: str
    mbid: str = ""
    url: str = ""
    playcount: int = 0
    listeners: int = 0
    image: Optional[LastFmImage] = None
    
    @validator('playcount', 'listeners', pre=True)
    def convert_to_int(cls, v):
        """Convert string numbers to integers"""
        if isinstance(v, str):
            return int(v) if v.isdigit() else 0
        return v or 0
    
    @classmethod
    def from_lastfm_chart(cls, chart_data: Dict[str, Any]) -> "ChartArtist":
        """Convert Last.fm chart artist to model"""
        return cls(
            name=chart_data.get("name", ""),
            mbid=chart_data.get("mbid", ""),
            url=chart_data.get("url", ""),
            playcount=chart_data.get("playcount", 0),
            listeners=chart_data.get("listeners", 0),
            image=LastFmImage.from_lastfm_images(chart_data.get("image", []))
        )
    
    def to_string(self) -> str:
        """Format chart artist information as string"""
        lines = [
            f"**{self.name}**",
            f"URL: {self.url}"
        ]
        
        if self.mbid:
            lines.append(f"MBID: {self.mbid}")
        if self.playcount > 0:
            lines.append(f"Playcount: {self.playcount:,}")
        if self.listeners > 0:
            lines.append(f"Listeners: {self.listeners:,}")
        
        return "\n".join(lines)


class ChartTrack(BaseModel):
    """Track from charts"""
    name: str
    artist: str
    mbid: str = ""
    url: str = ""
    playcount: int = 0
    listeners: int = 0
    image: Optional[LastFmImage] = None
    
    @validator('playcount', 'listeners', pre=True)
    def convert_to_int(cls, v):
        """Convert string numbers to integers"""
        if isinstance(v, str):
            return int(v) if v.isdigit() else 0
        return v or 0
    
    @classmethod
    def from_lastfm_chart(cls, chart_data: Dict[str, Any]) -> "ChartTrack":
        """Convert Last.fm chart track to model"""
        return cls(
            name=chart_data.get("name", ""),
            artist=chart_data.get("artist", {}).get("name", "") if isinstance(chart_data.get("artist"), dict) else str(chart_data.get("artist", "")),
            mbid=chart_data.get("mbid", ""),
            url=chart_data.get("url", ""),
            playcount=chart_data.get("playcount", 0),
            listeners=chart_data.get("listeners", 0),
            image=LastFmImage.from_lastfm_images(chart_data.get("image", []))
        )
    
    def to_string(self) -> str:
        """Format chart track information as string"""
        lines = [
            f"**{self.name}** by {self.artist}",
            f"URL: {self.url}"
        ]
        
        if self.mbid:
            lines.append(f"MBID: {self.mbid}")
        if self.playcount > 0:
            lines.append(f"Playcount: {self.playcount:,}")
        if self.listeners > 0:
            lines.append(f"Listeners: {self.listeners:,}")
        
        return "\n".join(lines)


class ChartTag(BaseModel):
    """Tag from charts"""
    name: str
    url: str = ""
    reach: int = 0
    taggings: int = 0
    
    @validator('reach', 'taggings', pre=True)
    def convert_to_int(cls, v):
        """Convert string numbers to integers"""
        if isinstance(v, str):
            return int(v) if v.isdigit() else 0
        return v or 0
    
    @classmethod
    def from_lastfm_chart(cls, chart_data: Dict[str, Any]) -> "ChartTag":
        """Convert Last.fm chart tag to model"""
        return cls(
            name=chart_data.get("name", ""),
            url=chart_data.get("url", ""),
            reach=chart_data.get("reach", 0),
            taggings=chart_data.get("taggings", 0)
        )
    
    def to_string(self) -> str:
        """Format chart tag information as string"""
        lines = [
            f"**#{self.name}**",
            f"URL: {self.url}"
        ]
        
        if self.reach > 0:
            lines.append(f"Reach: {self.reach:,}")
        if self.taggings > 0:
            lines.append(f"Taggings: {self.taggings:,}")
        
        return "\n".join(lines)


class ChartResponse(BaseModel):
    """Chart response with pagination"""
    page: int = 1
    per_page: int = 50
    total: int = 0
    total_pages: int = 1
    artists: List[ChartArtist] = Field(default_factory=list)
    
    def to_string(self) -> str:
        """Format chart response as string"""
        if not self.artists:
            return "No artists found in chart"
        
        lines = [
            f"**Global Top Artists Chart**",
            f"Total artists: {self.total:,}",
            f"Page {self.page} of {self.total_pages}",
            ""
        ]
        
        for i, artist in enumerate(self.artists, 1):
            lines.append(f"{i}. **{artist.name}**")
            if artist.playcount > 0:
                lines.append(f"   Playcount: {artist.playcount:,}")
            if artist.listeners > 0:
                lines.append(f"   Listeners: {artist.listeners:,}")
            lines.append("")
        
        return "\n".join(lines)


class ChartTracksResponse(BaseModel):
    """Chart tracks response with pagination"""
    page: int = 1
    per_page: int = 50
    total: int = 0
    total_pages: int = 1
    tracks: List[ChartTrack] = Field(default_factory=list)
    
    def to_string(self) -> str:
        """Format chart tracks response as string"""
        if not self.tracks:
            return "No tracks found in chart"
        
        lines = [
            f"**Global Top Tracks Chart**",
            f"Total tracks: {self.total:,}",
            f"Page {self.page} of {self.total_pages}",
            ""
        ]
        
        for i, track in enumerate(self.tracks, 1):
            lines.append(f"{i}. **{track.name}** by {track.artist}")
            if track.playcount > 0:
                lines.append(f"   Playcount: {track.playcount:,}")
            if track.listeners > 0:
                lines.append(f"   Listeners: {track.listeners:,}")
            lines.append("")
        
        return "\n".join(lines)


class ChartTagsResponse(BaseModel):
    """Chart tags response with pagination"""
    page: int = 1
    per_page: int = 50
    total: int = 0
    total_pages: int = 1
    tags: List[ChartTag] = Field(default_factory=list)
    
    def to_string(self) -> str:
        """Format chart tags response as string"""
        if not self.tags:
            return "No tags found in chart"
        
        lines = [
            f"**Global Top Tags Chart**",
            f"Total tags: {self.total:,}",
            f"Page {self.page} of {self.total_pages}",
            ""
        ]
        
        for i, tag in enumerate(self.tags, 1):
            lines.append(f"{i}. **#{tag.name}**")
            if tag.reach > 0:
                lines.append(f"   Reach: {tag.reach:,}")
            if tag.taggings > 0:
                lines.append(f"   Taggings: {tag.taggings:,}")
            lines.append("")
        
        return "\n".join(lines)
