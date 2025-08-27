"""
Tag-related Pydantic models
"""

from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field, validator
from src.models.base import LastFmImage


class Tag(BaseModel):
    """Tag information"""
    name: str
    url: str = ""
    reach: Optional[int] = None
    taggings: Optional[int] = None
    
    @validator('reach', 'taggings', pre=True)
    def convert_to_int(cls, v):
        """Convert string numbers to integers"""
        if v is None:
            return None
        if isinstance(v, str):
            return int(v) if v.isdigit() else 0
        return v or 0
    
    @classmethod
    def from_lastfm_tag(cls, tag_data: Dict[str, Any]) -> "Tag":
        """Convert Last.fm tag data to model"""
        return cls(
            name=tag_data.get("name", ""),
            url=tag_data.get("url", ""),
            reach=tag_data.get("reach"),
            taggings=tag_data.get("taggings")
        )
    
    def to_string(self) -> str:
        """Format tag information as string"""
        lines = [
            f"**#{self.name}**",
            f"URL: {self.url}"
        ]
        
        if self.reach:
            lines.append(f"Reach: {self.reach:,}")
        if self.taggings:
            lines.append(f"Taggings: {self.taggings:,}")
        
        return "\n".join(lines)


class TaggedArtist(BaseModel):
    """Artist with tag weight"""
    name: str
    mbid: str = ""
    url: str = ""
    streamable: bool = False
    image: Optional[LastFmImage] = None
    
    @classmethod
    def from_lastfm_tagged(cls, tagged_data: Dict[str, Any]) -> "TaggedArtist":
        """Convert Last.fm tagged artist to model"""
        return cls(
            name=tagged_data.get("name", ""),
            mbid=tagged_data.get("mbid", ""),
            url=tagged_data.get("url", ""),
            streamable=tagged_data.get("streamable", "0") == "1",
            image=LastFmImage.from_lastfm_images(tagged_data.get("image", []))
        )
    
    def to_string(self) -> str:
        """Format tagged artist information as string"""
        lines = [
            f"**{self.name}**",
            f"URL: {self.url}"
        ]
        
        if self.mbid:
            lines.append(f"MBID: {self.mbid}")
        if self.streamable:
            lines.append("Streamable: Yes")
        
        return "\n".join(lines)


class TaggedAlbum(BaseModel):
    """Album with tag weight"""
    name: str
    artist: str
    mbid: str = ""
    url: str = ""
    image: Optional[LastFmImage] = None
    
    @classmethod
    def from_lastfm_tagged(cls, tagged_data: Dict[str, Any]) -> "TaggedAlbum":
        """Convert Last.fm tagged album to model"""
        return cls(
            name=tagged_data.get("name", ""),
            artist=tagged_data.get("artist", {}).get("name", "") if isinstance(tagged_data.get("artist"), dict) else str(tagged_data.get("artist", "")),
            mbid=tagged_data.get("mbid", ""),
            url=tagged_data.get("url", ""),
            image=LastFmImage.from_lastfm_images(tagged_data.get("image", []))
        )
    
    def to_string(self) -> str:
        """Format tagged album information as string"""
        lines = [
            f"**{self.name}** by {self.artist}",
            f"URL: {self.url}"
        ]
        
        if self.mbid:
            lines.append(f"MBID: {self.mbid}")
        
        return "\n".join(lines)


class TaggedTrack(BaseModel):
    """Track with tag weight"""
    name: str
    artist: str
    mbid: str = ""
    url: str = ""
    duration: Optional[int] = None
    image: Optional[LastFmImage] = None
    
    @validator('duration', pre=True)
    def convert_duration(cls, v):
        """Convert duration to int"""
        if v is None:
            return None
        if isinstance(v, str):
            return int(v) if v.isdigit() else None
        return v
    
    @classmethod
    def from_lastfm_tagged(cls, tagged_data: Dict[str, Any]) -> "TaggedTrack":
        """Convert Last.fm tagged track to model"""
        return cls(
            name=tagged_data.get("name", ""),
            artist=tagged_data.get("artist", {}).get("name", "") if isinstance(tagged_data.get("artist"), dict) else str(tagged_data.get("artist", "")),
            mbid=tagged_data.get("mbid", ""),
            url=tagged_data.get("url", ""),
            duration=tagged_data.get("duration"),
            image=LastFmImage.from_lastfm_images(tagged_data.get("image", []))
        )
    
    def to_string(self) -> str:
        """Format tagged track information as string"""
        lines = [
            f"**{self.name}** by {self.artist}",
            f"URL: {self.url}"
        ]
        
        if self.mbid:
            lines.append(f"MBID: {self.mbid}")
        if self.duration:
            minutes = self.duration // 60
            seconds = self.duration % 60
            lines.append(f"Duration: {minutes}:{seconds:02d}")
        
        return "\n".join(lines)


class WeeklyChart(BaseModel):
    """Weekly chart period"""
    from_date: str = ""
    to_date: str = ""
    text: str = ""
    
    @classmethod
    def from_lastfm_weekly_chart(cls, chart_data: Dict[str, Any]) -> "WeeklyChart":
        """Convert Last.fm weekly chart data to model"""
        return cls(
            from_date=chart_data.get("from", ""),
            to_date=chart_data.get("to", ""),
            text=chart_data.get("#text", "")
        )
    
    def to_string(self) -> str:
        """Format weekly chart as string"""
        return f"{self.text} (from {self.from_date} to {self.to_date})"


class TagTopArtistsResponse(BaseModel):
    """Response for tag.getTopArtists"""
    tag: str = ""
    total: int = 0
    page: int = 1
    per_page: int = 50
    artists: List[TaggedArtist] = Field(default_factory=list)
    
    def to_string(self) -> str:
        """Format tag top artists response as string"""
        if not self.artists:
            return f"No artists found for tag '{self.tag}'"
        
        lines = [
            f"**Top Artists for #{self.tag}**",
            f"Total artists: {self.total:,}",
            f"Page {self.page} of {self.total // self.per_page + 1 if self.total % self.per_page else self.total // self.per_page}",
            ""
        ]
        
        for i, artist in enumerate(self.artists, 1):
            lines.append(f"{i}. {artist.name}")
            lines.append(f"   URL: {artist.url}")
            if artist.mbid:
                lines.append(f"   MBID: {artist.mbid}")
            lines.append("")
        
        return "\n".join(lines)


class TagTopAlbumsResponse(BaseModel):
    """Response for tag.getTopAlbums"""
    tag: str = ""
    total: int = 0
    page: int = 1
    per_page: int = 50
    albums: List[TaggedAlbum] = Field(default_factory=list)
    
    def to_string(self) -> str:
        """Format tag top albums response as string"""
        if not self.albums:
            return f"No albums found for tag '{self.tag}'"
        
        lines = [
            f"**Top Albums for #{self.tag}**",
            f"Total albums: {self.total:,}",
            f"Page {self.page} of {self.total // self.per_page + 1 if self.total % self.per_page else self.total // self.per_page}",
            ""
        ]
        
        for i, album in enumerate(self.albums, 1):
            lines.append(f"{i}. **{album.name}** by {album.artist}")
            if album.mbid:
                lines.append(f"   MBID: {album.mbid}")
            lines.append("")
        
        return "\n".join(lines)


class TagTopTracksResponse(BaseModel):
    """Response for tag.getTopTracks"""
    tag: str = ""
    total: int = 0
    page: int = 1
    per_page: int = 50
    tracks: List[TaggedTrack] = Field(default_factory=list)
    
    def to_string(self) -> str:
        """Format tag top tracks response as string"""
        if not self.tracks:
            return f"No tracks found for tag '{self.tag}'"
        
        lines = [
            f"**Top Tracks for #{self.tag}**",
            f"Total tracks: {self.total:,}",
            f"Page {self.page} of {self.total // self.per_page + 1 if self.total % self.per_page else self.total // self.per_page}",
            ""
        ]
        
        for i, track in enumerate(self.tracks, 1):
            lines.append(f"{i}. **{track.name}** by {track.artist}")
            if track.duration:
                minutes = track.duration // 60
                seconds = track.duration % 60
                lines.append(f"   Duration: {minutes}:{seconds:02d}")
            lines.append("")
        
        return "\n".join(lines)


class TagWeeklyChartListResponse(BaseModel):
    """Response for tag.getWeeklyChartList"""
    tag: str = ""
    charts: List[WeeklyChart] = Field(default_factory=list)
    
    def to_string(self) -> str:
        """Format tag weekly chart list response as string"""
        if not self.charts:
            return f"No weekly charts found for tag '{self.tag}'"
        
        lines = [
            f"**Weekly Charts for #{self.tag}**",
            f"Available chart periods:",
            ""
        ]
        
        for i, chart in enumerate(self.charts, 1):
            lines.append(f"{i}. {chart.to_string()}")
            lines.append("")
        
        return "\n".join(lines)
