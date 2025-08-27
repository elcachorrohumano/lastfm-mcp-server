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
    
    def to_string(self) -> str:
        """Format track information as string"""
        lines = [
            f"**{self.name}** by {self.artist}",
            f"URL: {self.url}"
        ]
        
        if self.mbid:
            lines.append(f"MBID: {self.mbid}")
        if self.album:
            lines.append(f"Album: {self.album}")
        if self.duration:
            minutes = self.duration // 60
            seconds = self.duration % 60
            lines.append(f"Duration: {minutes}:{seconds:02d}")
        if self.playcount > 0:
            lines.append(f"Playcount: {self.playcount:,}")
        if self.listeners:
            lines.append(f"Listeners: {self.listeners:,}")
        
        # Add wiki summary
        if self.wiki:
            lines.append(f"\n**Summary:**")
            lines.append(self.wiki)
        
        # Add tags
        if self.tags:
            lines.append(f"\n**Tags:** {', '.join(self.tags[:10])}")
            if len(self.tags) > 10:
                lines.append(f"... and {len(self.tags) - 10} more")
        
        return "\n".join(lines)


class TrackListResponse(BaseModel):
    """Response for track lists (top tracks, etc.)"""
    artist: str = ""
    total: int = 0
    page: int = 1
    per_page: int = 50
    tracks: List[Track] = Field(default_factory=list)
    
    def to_string(self) -> str:
        """Format track list response as string"""
        if not self.tracks:
            return f"No tracks found for {self.artist}"
        
        lines = [
            f"**Top Tracks for {self.artist}**",
            f"Total tracks: {self.total:,}",
            f"Page {self.page} of {self.total // self.per_page + 1 if self.total % self.per_page else self.total // self.per_page}",
            ""
        ]
        
        for i, track in enumerate(self.tracks, 1):
            lines.append(f"{i}. **{track.name}**")
            if track.playcount > 0:
                lines.append(f"   Plays: {track.playcount:,}")
            if track.listeners:
                lines.append(f"   Listeners: {track.listeners:,}")
            if track.album:
                lines.append(f"   Album: {track.album}")
            lines.append("")
        
        return "\n".join(lines)


class TrackSearchResult(BaseModel):
    """Single track from search results"""
    name: str
    artist: str
    mbid: str = ""
    url: str = ""
    listeners: int = 0
    image: Optional[LastFmImage] = None
    
    def to_string(self, index: Optional[int] = None) -> str:
        """Format track search result as string"""
        listeners = f"{self.listeners:,}" if self.listeners > 0 else "Unknown"
        mbid_info = f" (MBID: {self.mbid})" if self.mbid else ""
        
        prefix = f"{index}. " if index is not None else ""
        
        return (
            f"{prefix}**{self.name}** by {self.artist}{mbid_info}\n"
            f"Listeners: {listeners}\n"
            f"URL: {self.url}"
        )
    
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
    
    def to_string(self) -> str:
        """Format track search response as string"""
        if not self.tracks:
            return f"No tracks found for '{self.query}'"
        
        lines = [
            f"Found {len(self.tracks)} tracks for '{self.query}':",
            f"Total results available: {self.total_results:,}",
            ""
        ]
        
        for i, track in enumerate(self.tracks, 1):
            lines.append(track.to_string(index=i))
        
        # Add helpful tip if there are more results
        if len(self.tracks) == self.items_per_page and self.total_results > len(self.tracks):
            lines.append(f"\nShowing first {len(self.tracks)} results. Use get_track_info() to learn more about specific tracks.")
        
        return "\n".join(lines)


class TrackSimilarResponse(BaseModel):
    """Response for track.getSimilar"""
    artist: str = ""
    track: str = ""
    similar: List[Dict[str, Any]] = Field(default_factory=list)
    
    def to_string(self) -> str:
        """Format track similar response as string"""
        if not self.similar:
            return f"No similar tracks found for '{self.track}' by {self.artist}"
        
        lines = [
            f"**Tracks Similar to '{self.track}' by {self.artist}**",
            f"Found {len(self.similar)} similar tracks:",
            ""
        ]
        
        for i, similar in enumerate(self.similar, 1):
            lines.append(f"{i}. **{similar['name']}** by {similar['artist']}")
            lines.append(f"   Match: {similar['match']:.1%}")
            if similar.get('duration'):
                minutes = similar['duration'] // 60
                seconds = similar['duration'] % 60
                lines.append(f"   Duration: {minutes}:{seconds:02d}")
            lines.append("")
        
        return "\n".join(lines)


class TrackTopTagsResponse(BaseModel):
    """Response for track.getTopTags"""
    artist: str = ""
    track: str = ""
    tags: List[Dict[str, Any]] = Field(default_factory=list)
    
    def to_string(self) -> str:
        """Format track top tags response as string"""
        if not self.tags:
            return f"No tags found for '{self.track}' by {self.artist}"
        
        lines = [
            f"**Top Tags for '{self.track}' by {self.artist}**",
            ""
        ]
        
        for i, tag in enumerate(self.tags, 1):
            lines.append(f"{i}. **#{tag['name']}** ({tag['count']:,} times)")
        
        return "\n".join(lines)
