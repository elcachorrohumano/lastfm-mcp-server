"""
Album-related Pydantic models
"""

from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field, validator
from src.models.base import LastFmImage


class Album(BaseModel):
    """Album information"""
    name: str
    artist: str
    mbid: str = ""
    url: str = ""
    playcount: int = 0
    listeners: Optional[int] = None
    image: Optional[LastFmImage] = None
    tags: List[str] = Field(default_factory=list)
    wiki: Optional[str] = None
    
    @validator('playcount', 'listeners', pre=True)
    def convert_to_int(cls, v):
        """Convert string numbers to integers"""
        if v is None:
            return None
        if isinstance(v, str):
            return int(v) if v.isdigit() else 0
        return v or 0
    
    @classmethod
    def from_lastfm_album(cls, album_data: Dict[str, Any]) -> "Album":
        """Convert Last.fm album data to model"""
        # Handle artist field (can be string or dict)
        artist_data = album_data.get("artist", "")
        if isinstance(artist_data, dict):
            artist_name = artist_data.get("name", "")
        else:
            artist_name = str(artist_data)
        
        # Extract tags
        tags_data = album_data.get("tags", {}).get("tag", [])
        if isinstance(tags_data, dict):  # Single tag
            tags_data = [tags_data]
        tags = [tag.get("name", "") for tag in tags_data if isinstance(tag, dict)]
        
        # Extract wiki
        wiki_data = album_data.get("wiki", {})
        wiki = wiki_data.get("summary", "") if wiki_data else None
        
        return cls(
            name=album_data.get("name", ""),
            artist=artist_name,
            mbid=album_data.get("mbid", ""),
            url=album_data.get("url", ""),
            playcount=album_data.get("playcount", 0),
            listeners=album_data.get("listeners"),
            image=LastFmImage.from_lastfm_images(album_data.get("image", [])),
            tags=tags,
            wiki=wiki
        )
    def to_string(self) -> str:
        """Format album as string"""
        lines = [
            f"**{self.name}**",
            f"Artist: {self.artist}",
            f"Playcount: {self.playcount:,}"
        ]
        if self.listeners:
            lines.append(f"Listeners: {self.listeners:,}")
        if self.image and self.image.large:
            lines.append(f"Image: {self.image.large}")
        if self.tags:
            lines.append(f"Tags: {', '.join(self.tags[:10])}")
        if self.wiki:
            lines.append(f"**Biography:**")
            lines.append(self.wiki)
        return "\n".join(lines)


class AlbumListResponse(BaseModel):
    """Response for album lists (top albums, etc.)"""
    artist: str = ""
    total: int = 0
    page: int = 1
    per_page: int = 50
    albums: List[Album] = Field(default_factory=list)

    def to_string(self) -> str:
        """Format album list as string"""
        if not self.albums:
            return f"No albums found for {self.artist}"
        
        lines = [
            f"**Top Albums for {self.artist}**",
            f"Total albums: {self.total:,}",
            f"Page {self.page} of {self.total // self.per_page + 1 if self.total % self.per_page else self.total // self.per_page}",
            ""
        ]

        for i, album in enumerate(self.albums, 1):
            lines.append(f"{i}. **{album.name}**")
            if album.artist:
                lines.append(f"   Artist: {album.artist}")
            if album.playcount > 0:
                lines.append(f"   Plays: {album.playcount:,}")
            if album.listeners:
                lines.append(f"   Listeners: {album.listeners:,}")
            if album.mbid:
                lines.append(f"   MBID: {album.mbid}")
            lines.append("")

        return "\n".join(lines)


class AlbumSearchResult(BaseModel):
    """Single album from search results"""
    name: str
    artist: str
    mbid: str = ""
    url: str = ""
    listeners: int = 0
    image: Optional[LastFmImage] = None
    
    @validator('listeners', pre=True)
    def convert_listeners(cls, v):
        """Convert listeners to int"""
        if isinstance(v, str):
            return int(v) if v.isdigit() else 0
        return v or 0
    
    @classmethod
    def from_lastfm_search(cls, search_data: Dict[str, Any]) -> "AlbumSearchResult":
        """Convert Last.fm search result to model"""
        return cls(
            name=search_data.get("name", ""),
            artist=search_data.get("artist", ""),
            mbid=search_data.get("mbid", ""),
            url=search_data.get("url", ""),
            listeners=search_data.get("listeners", 0),
            image=LastFmImage.from_lastfm_images(search_data.get("image", []))
        )


class AlbumSearchResponse(BaseModel):
    """Album search response with pagination"""
    query: str = ""
    total_results: int = 0
    start_page: int = 1
    items_per_page: int = 30
    albums: List[AlbumSearchResult] = Field(default_factory=list)
    
    def to_string(self) -> str:
        """Format album search response as string"""
        if not self.albums:
            return f"No albums found for '{self.query}'"
        
        lines = [
            f"Found {len(self.albums)} albums for '{self.query}':",
            f"Total results available: {self.total_results:,}",
            ""
        ]
        
        for i, album in enumerate(self.albums, 1):
            listeners = f"{album.listeners:,}" if album.listeners > 0 else "Unknown"
            mbid_info = f" (MBID: {album.mbid})" if album.mbid else ""
            
            lines.append(f"{i}. **{album.name}** by {album.artist}{mbid_info}")
            lines.append(f"   Listeners: {listeners}")
            lines.append(f"   URL: {album.url}")
            lines.append("")
        
        # Add helpful tip if there are more results
        if len(self.albums) == self.items_per_page and self.total_results > len(self.albums):
            lines.append(f"Showing first {len(self.albums)} results. Use get_album_info() to learn more about specific albums.")
        
        return "\n".join(lines)


class AlbumTopTagsResponse(BaseModel):
    """Response for album.getTopTags"""
    artist: str = ""
    album: str = ""
    tags: List[Dict[str, Any]] = Field(default_factory=list)
    
    def to_string(self) -> str:
        """Format album top tags response as string"""
        if not self.tags:
            return f"No tags found for '{self.album}' by {self.artist}"
        
        lines = [
            f"**Top Tags for '{self.album}' by {self.artist}**",
            ""
        ]
        
        for i, tag in enumerate(self.tags, 1):
            lines.append(f"{i}. **#{tag['name']}** ({tag['count']:,} times)")
        
        return "\n".join(lines)
