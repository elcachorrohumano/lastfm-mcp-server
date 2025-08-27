"""
Last.fm API Pydantic models
Organized by endpoint for better maintainability
"""

from src.models.base import LastFmImage, LastFmStats, LastFmDate
from src.models.artist import ArtistInfo, ArtistBiography, SimilarArtist, ArtistSearchResult, ArtistSearchResponse
from src.models.album import Album, AlbumListResponse, AlbumSearchResult, AlbumSearchResponse
from src.models.track import Track, TrackListResponse, TrackSearchResult, TrackSearchResponse
from src.models.user import UserInfo, Scrobble, RecentTracksResponse
from src.models.tag import Tag, TaggedArtist, TagTopArtistsResponse
from src.models.chart import ChartArtist, ChartResponse

__all__ = [
    # Base models
    "LastFmImage",
    "LastFmStats", 
    "LastFmDate",
    
    # Artist models
    "ArtistInfo",
    "ArtistBiography",
    "SimilarArtist", 
    "ArtistSearchResult",
    "ArtistSearchResponse",
    
    # Album models
    "Album",
    "AlbumListResponse",
    "AlbumSearchResult",
    "AlbumSearchResponse",
    
    # Track models
    "Track",
    "TrackListResponse",
    "TrackSearchResult", 
    "TrackSearchResponse",
    
    # User models
    "UserInfo",
    "Scrobble",
    "RecentTracksResponse",
    
    # Tag models
    "Tag",
    "TaggedArtist",
    "TagTopArtistsResponse",
    
    # Chart models
    "ChartArtist",
    "ChartResponse",
]
