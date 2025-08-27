"""
Artist-related Pydantic models
"""

from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field, validator
from src.models.base import LastFmImage, LastFmStats


class ArtistBiography(BaseModel):
    """Artist biography information"""
    published: str = ""
    summary: str = ""
    content: str = ""
    
    @validator('published', 'summary', 'content', pre=True)
    def clean_text(cls, v):
        """Clean up text fields"""
        return v.strip() if isinstance(v, str) else ""


class SimilarArtist(BaseModel):
    """Similar artist information"""
    name: str
    url: str = ""
    image: Optional[LastFmImage] = None
    
    @classmethod
    def from_lastfm_similar(cls, similar_data: Dict[str, Any]) -> "SimilarArtist":
        """Convert Last.fm similar artist data"""
        return cls(
            name=similar_data.get("name", ""),
            url=similar_data.get("url", ""),
            image=LastFmImage.from_lastfm_images(similar_data.get("image", []))
        )


class Artist(BaseModel):
    """Complete artist information"""
    name: str
    mbid: str = ""
    url: str = ""
    stats: LastFmStats = Field(default_factory=LastFmStats)
    biography: Optional[ArtistBiography] = None
    image: Optional[LastFmImage] = None
    tags: List[str] = Field(default_factory=list)
    similar: List[SimilarArtist] = Field(default_factory=list)
    
    @classmethod
    def from_lastfm_artist(cls, artist_data: Dict[str, Any]) -> "Artist":
        """Convert Last.fm artist.getinfo response to Artist model"""
        # Extract stats
        stats_data = artist_data.get("stats", {})
        stats = LastFmStats(
            listeners=stats_data.get("listeners", 0),
            playcount=stats_data.get("playcount", 0)
        )
        
        # Extract biography
        bio_data = artist_data.get("bio", {})
        biography = ArtistBiography(
            published=bio_data.get("published", ""),
            summary=bio_data.get("summary", ""),
            content=bio_data.get("content", "")
        ) if bio_data else None
        
        # Extract images
        image = LastFmImage.from_lastfm_images(artist_data.get("image", []))
        
        # Extract tags
        tags_data = artist_data.get("tags", {}).get("tag", [])
        if isinstance(tags_data, dict):  # Single tag
            tags_data = [tags_data]
        tags = [tag.get("name", "") for tag in tags_data if isinstance(tag, dict)]
        
        # Extract similar artists
        similar_data = artist_data.get("similar", {}).get("artist", [])
        if isinstance(similar_data, dict):  # Single similar artist
            similar_data = [similar_data]
        similar = [SimilarArtist.from_lastfm_similar(s) for s in similar_data if isinstance(s, dict)]
        
        return cls(
            name=artist_data.get("name", ""),
            mbid=artist_data.get("mbid", ""),
            url=artist_data.get("url", ""),
            stats=stats,
            biography=biography,
            image=image,
            tags=tags,
            similar=similar
        )


class ArtistSearchResult(BaseModel):
    """Single artist from search results"""
    name: str
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
    
    def to_string(self, index: Optional[int] = None) -> str:
        """Format artist search result as string"""
        listeners = f"{self.listeners:,}" if self.listeners > 0 else "Unknown"
        mbid_info = f" (MBID: {self.mbid})" if self.mbid else ""
        
        prefix = f"{index}. " if index is not None else ""
        
        return (
            f"{prefix}**{self.name}**{mbid_info}\n"
            f"Listeners: {listeners}\n"
            f"URL: {self.url}"
        )
    
    @classmethod
    def from_lastfm_search(cls, search_data: Dict[str, Any]) -> "ArtistSearchResult":
        """Convert Last.fm search result to model"""
        return cls(
            name=search_data.get("name", ""),
            mbid=search_data.get("mbid", ""),
            url=search_data.get("url", ""),
            listeners=search_data.get("listeners", 0),
            image=LastFmImage.from_lastfm_images(search_data.get("image", []))
        )


class ArtistSearchResponse(BaseModel):
    """Artist search response with pagination"""
    query: str = ""
    total_results: int = 0
    start_page: int = 1
    items_per_page: int = 30
    artists: List[ArtistSearchResult] = Field(default_factory=list)
    
    def to_string(self) -> str:
        """Format artist search response as string"""
        if not self.artists:
            return f"No artists found for '{self.query}'"
        
        response_lines = [
            f"Found {len(self.artists)} artists for '{self.query}':",
            f"Total results available: {self.total_results:,}",
            ""
        ]
        
        for i, artist in enumerate(self.artists, 1):
            response_lines.append(artist.to_string(index=i))
        
        # Add helpful tip if there are more results
        if len(self.artists) == self.items_per_page and self.total_results > len(self.artists):
            response_lines.append(f"\nShowing first {len(self.artists)} results. Use get_artist_info() to learn more about specific artists.")
        
        return "\n".join(response_lines)
