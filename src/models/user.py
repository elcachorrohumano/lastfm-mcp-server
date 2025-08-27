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
    registered: Optional[LastFmDate] = None
    image: Optional[LastFmImage] = None
    
    @validator('playcount', 'playlists', 'age', pre=True)
    def convert_to_int(cls, v):
        """Convert string numbers to integers"""
        if v is None:
            return None
        if isinstance(v, str):
            return int(v) if v.isdigit() else 0
        return v or 0
    
    @classmethod
    def from_lastfm_user(cls, user_data: Dict[str, Any]) -> "UserInfo":
        """Convert Last.fm user data to model"""
        registered_data = user_data.get("registered", {})
        # Handle case where registered is an integer timestamp
        if isinstance(registered_data, int):
            registered_data = {"uts": registered_data}
        
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
            registered=LastFmDate.from_lastfm_date(registered_data),
            image=LastFmImage.from_lastfm_images(user_data.get("image", []))
        )
    
    def to_string(self) -> str:
        """Format user information as string"""
        lines = [
            f"**{self.name}**",
            f"URL: {self.url}"
        ]
        
        if self.realname:
            lines.append(f"Real name: {self.realname}")
        if self.country:
            lines.append(f"Country: {self.country}")
        if self.age:
            lines.append(f"Age: {self.age}")
        if self.gender:
            lines.append(f"Gender: {self.gender}")
        
        lines.append(f"Subscriber: {'Yes' if self.subscriber else 'No'}")
        lines.append(f"Total playcount: {self.playcount:,}")
        lines.append(f"Playlists: {self.playlists}")
        
        if self.registered and self.registered.timestamp:
            from datetime import datetime
            reg_date = datetime.fromtimestamp(self.registered.timestamp)
            lines.append(f"Registered: {reg_date.strftime('%B %d, %Y')}")
        
        return "\n".join(lines)


class Scrobble(BaseModel):
    """Scrobbled track information"""
    track: str
    artist: str
    album: Optional[str] = None
    mbid: str = ""
    url: str = ""
    image: Optional[LastFmImage] = None
    date: Optional[LastFmDate] = None
    nowplaying: bool = False
    
    @classmethod
    def from_lastfm_scrobble(cls, scrobble_data: Dict[str, Any]) -> "Scrobble":
        """Convert Last.fm scrobble data to model"""
        nowplaying = scrobble_data.get("@attr", {}).get("nowplaying", "false") == "true"
        
        return cls(
            track=scrobble_data.get("name", ""),
            artist=scrobble_data.get("artist", {}).get("#text", "") if isinstance(scrobble_data.get("artist"), dict) else str(scrobble_data.get("artist", "")),
            album=scrobble_data.get("album", {}).get("#text", "") if isinstance(scrobble_data.get("album"), dict) else str(scrobble_data.get("album", "")) if scrobble_data.get("album") else None,
            mbid=scrobble_data.get("mbid", ""),
            url=scrobble_data.get("url", ""),
            image=LastFmImage.from_lastfm_images(scrobble_data.get("image", [])),
            date=LastFmDate.from_lastfm_date(scrobble_data.get("date", {})) if not nowplaying else None,
            nowplaying=nowplaying
        )
    
    def to_string(self) -> str:
        """Format scrobble information as string"""
        status = "🎵 Now Playing" if self.nowplaying else "📝 Scrobbled"
        
        lines = [
            f"{status} **{self.track}** by {self.artist}"
        ]
        
        if self.album:
            lines.append(f"Album: {self.album}")
        if self.mbid:
            lines.append(f"MBID: {self.mbid}")
        
        if self.date and self.date.text:
            lines.append(f"Date: {self.date.text}")
        
        return "\n".join(lines)


class UserTopArtist(BaseModel):
    """User's top artist"""
    name: str
    mbid: str = ""
    url: str = ""
    playcount: int = 0
    rank: int = 0
    image: Optional[LastFmImage] = None
    
    @validator('playcount', 'rank', pre=True)
    def convert_to_int(cls, v):
        """Convert string numbers to integers"""
        if isinstance(v, str):
            return int(v) if v.isdigit() else 0
        return v or 0
    
    @classmethod
    def from_lastfm_top(cls, top_data: Dict[str, Any]) -> "UserTopArtist":
        """Convert Last.fm top artist data to model"""
        return cls(
            name=top_data.get("name", ""),
            mbid=top_data.get("mbid", ""),
            url=top_data.get("url", ""),
            playcount=top_data.get("playcount", 0),
            rank=top_data.get("@attr", {}).get("rank", 0),
            image=LastFmImage.from_lastfm_images(top_data.get("image", []))
        )
    
    def to_string(self) -> str:
        """Format user top artist as string"""
        lines = [
            f"**{self.name}**",
            f"Playcount: {self.playcount:,}",
            f"Rank: #{self.rank}"
        ]
        
        if self.mbid:
            lines.append(f"MBID: {self.mbid}")
        if self.url:
            lines.append(f"URL: {self.url}")
        
        return "\n".join(lines)


class UserTopAlbum(BaseModel):
    """User's top album"""
    name: str
    artist: str
    mbid: str = ""
    url: str = ""
    playcount: int = 0
    rank: int = 0
    image: Optional[LastFmImage] = None
    
    @validator('playcount', 'rank', pre=True)
    def convert_to_int(cls, v):
        """Convert string numbers to integers"""
        if isinstance(v, str):
            return int(v) if v.isdigit() else 0
        return v or 0
    
    @classmethod
    def from_lastfm_top(cls, top_data: Dict[str, Any]) -> "UserTopAlbum":
        """Convert Last.fm top album data to model"""
        return cls(
            name=top_data.get("name", ""),
            artist=top_data.get("artist", {}).get("name", "") if isinstance(top_data.get("artist"), dict) else str(top_data.get("artist", "")),
            mbid=top_data.get("mbid", ""),
            url=top_data.get("url", ""),
            playcount=top_data.get("playcount", 0),
            rank=top_data.get("@attr", {}).get("rank", 0),
            image=LastFmImage.from_lastfm_images(top_data.get("image", []))
        )
    
    def to_string(self) -> str:
        """Format user top album as string"""
        lines = [
            f"**{self.name}** by {self.artist}",
            f"Playcount: {self.playcount:,}",
            f"Rank: #{self.rank}"
        ]
        
        if self.mbid:
            lines.append(f"MBID: {self.mbid}")
        if self.url:
            lines.append(f"URL: {self.url}")
        
        return "\n".join(lines)


class UserTopTrack(BaseModel):
    """User's top track"""
    name: str
    artist: str
    mbid: str = ""
    url: str = ""
    playcount: int = 0
    rank: int = 0
    image: Optional[LastFmImage] = None
    
    @validator('playcount', 'rank', pre=True)
    def convert_to_int(cls, v):
        """Convert string numbers to integers"""
        if isinstance(v, str):
            return int(v) if v.isdigit() else 0
        return v or 0
    
    @classmethod
    def from_lastfm_top(cls, top_data: Dict[str, Any]) -> "UserTopTrack":
        """Convert Last.fm top track data to model"""
        return cls(
            name=top_data.get("name", ""),
            artist=top_data.get("artist", {}).get("name", "") if isinstance(top_data.get("artist"), dict) else str(top_data.get("artist", "")),
            mbid=top_data.get("mbid", ""),
            url=top_data.get("url", ""),
            playcount=top_data.get("playcount", 0),
            rank=top_data.get("@attr", {}).get("rank", 0),
            image=LastFmImage.from_lastfm_images(top_data.get("image", []))
        )
    
    def to_string(self) -> str:
        """Format user top track as string"""
        lines = [
            f"**{self.name}** by {self.artist}",
            f"Playcount: {self.playcount:,}",
            f"Rank: #{self.rank}"
        ]
        
        if self.mbid:
            lines.append(f"MBID: {self.mbid}")
        if self.url:
            lines.append(f"URL: {self.url}")
        
        return "\n".join(lines)


class LovedTrack(BaseModel):
    """User's loved track"""
    name: str
    artist: str
    mbid: str = ""
    url: str = ""
    date: Optional[LastFmDate] = None
    image: Optional[LastFmImage] = None
    
    @classmethod
    def from_lastfm_loved(cls, loved_data: Dict[str, Any]) -> "LovedTrack":
        """Convert Last.fm loved track data to model"""
        return cls(
            name=loved_data.get("name", ""),
            artist=loved_data.get("artist", {}).get("name", "") if isinstance(loved_data.get("artist"), dict) else str(loved_data.get("artist", "")),
            mbid=loved_data.get("mbid", ""),
            url=loved_data.get("url", ""),
            date=LastFmDate.from_lastfm_date(loved_data.get("date", {})),
            image=LastFmImage.from_lastfm_images(loved_data.get("image", []))
        )
    
    def to_string(self) -> str:
        """Format loved track as string"""
        lines = [
            f"❤️ **{self.name}** by {self.artist}"
        ]
        
        if self.mbid:
            lines.append(f"MBID: {self.mbid}")
        if self.url:
            lines.append(f"URL: {self.url}")
        if self.date and self.date.text:
            lines.append(f"Loved on: {self.date.text}")
        
        return "\n".join(lines)


class RecentTracksResponse(BaseModel):
    """User's recent tracks response"""
    user: str = ""
    total: int = 0
    page: int = 1
    per_page: int = 50
    total_pages: int = 1
    tracks: List[Scrobble] = Field(default_factory=list)
    
    def to_string(self) -> str:
        """Format recent tracks response as string"""
        if not self.tracks:
            return f"No recent tracks found for {self.user}"
        
        lines = [
            f"**Recent Tracks for {self.user}**",
            f"Total scrobbles: {self.total:,}",
            f"Page {self.page} of {self.total_pages}",
            ""
        ]
        
        for i, track in enumerate(self.tracks, 1):
            lines.append(f"{i}. {track.to_string()}")
            lines.append("")
        
        return "\n".join(lines)


class UserTopArtistsResponse(BaseModel):
    """User's top artists response"""
    user: str = ""
    period: str = "overall"
    total: int = 0
    page: int = 1
    per_page: int = 50
    total_pages: int = 1
    artists: List[UserTopArtist] = Field(default_factory=list)
    
    def to_string(self) -> str:
        """Format user top artists response as string"""
        if not self.artists:
            return f"No top artists found for user '{self.user}'"
        
        lines = [
            f"**Top Artists for {self.user}** ({self.period})",
            f"Page {self.page} of {self.total_pages}",
            f"Total artists: {self.total:,}",
            ""
        ]
        
        for i, artist in enumerate(self.artists, 1):
            lines.append(f"{i}. {artist.to_string()}")
            lines.append("")
        
        return "\n".join(lines)


class UserTopAlbumsResponse(BaseModel):
    """User's top albums response"""
    user: str = ""
    period: str = "overall"
    total: int = 0
    page: int = 1
    per_page: int = 50
    total_pages: int = 1
    albums: List[UserTopAlbum] = Field(default_factory=list)
    
    def to_string(self) -> str:
        """Format user top albums response as string"""
        if not self.albums:
            return f"No top albums found for user '{self.user}'"
        
        lines = [
            f"**Top Albums for {self.user}** ({self.period})",
            f"Page {self.page} of {self.total_pages}",
            f"Total albums: {self.total:,}",
            ""
        ]
        
        for i, album in enumerate(self.albums, 1):
            lines.append(f"{i}. {album.to_string()}")
            lines.append("")
        
        return "\n".join(lines)


class UserTopTracksResponse(BaseModel):
    """User's top tracks response"""
    user: str = ""
    period: str = "overall"
    total: int = 0
    page: int = 1
    per_page: int = 50
    total_pages: int = 1
    tracks: List[UserTopTrack] = Field(default_factory=list)
    
    def to_string(self) -> str:
        """Format user top tracks response as string"""
        if not self.tracks:
            return f"No top tracks found for user '{self.user}'"
        
        lines = [
            f"**Top Tracks for {self.user}** ({self.period})",
            f"Page {self.page} of {self.total_pages}",
            f"Total tracks: {self.total:,}",
            ""
        ]
        
        for i, track in enumerate(self.tracks, 1):
            lines.append(f"{i}. {track.to_string()}")
            lines.append("")
        
        return "\n".join(lines)


class UserLovedTracksResponse(BaseModel):
    """User's loved tracks response"""
    user: str = ""
    total: int = 0
    page: int = 1
    per_page: int = 50
    total_pages: int = 1
    tracks: List[LovedTrack] = Field(default_factory=list)
    
    def to_string(self) -> str:
        """Format user loved tracks response as string"""
        if not self.tracks:
            return f"No loved tracks found for user '{self.user}'"
        
        lines = [
            f"**Loved Tracks for {self.user}** ❤️",
            f"Page {self.page} of {self.total_pages}",
            f"Total loved tracks: {self.total:,}",
            ""
        ]
        
        for i, track in enumerate(self.tracks, 1):
            lines.append(f"{i}. {track.to_string()}")
            lines.append("")
        
        return "\n".join(lines)
