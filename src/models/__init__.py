"""
Last.fm API Pydantic models
Organized by endpoint for better maintainability
"""

from src.models.base import LastFmImage, LastFmStats, LastFmDate
from src.models.artist import ArtistInfo, ArtistBiography, SimilarArtist, ArtistSearchResult, ArtistSearchResponse
from src.models.album import Album, AlbumListResponse, AlbumSearchResult, AlbumSearchResponse, AlbumTopTagsResponse
from src.models.track import (
    Track, TrackListResponse, TrackSearchResult, TrackSearchResponse, TrackSimilarResponse, TrackTopTagsResponse,
    TrackScrobbleResponse, TrackNowPlayingResponse, TrackLoveResponse, TrackUnloveResponse, TrackAddTagsResponse, TrackRemoveTagResponse
)
from src.models.user import (
    UserInfo, Scrobble, RecentTracksResponse, 
    UserTopArtist, UserTopAlbum, UserTopTrack, LovedTrack,
    UserTopArtistsResponse, UserTopAlbumsResponse, UserTopTracksResponse, UserLovedTracksResponse
)
from src.models.tag import (
    Tag, TaggedArtist, TaggedAlbum, TaggedTrack, WeeklyChart,
    TagTopArtistsResponse, TagTopAlbumsResponse, TagTopTracksResponse, TagWeeklyChartListResponse
)
from src.models.chart import (
    ChartArtist, ChartTrack, ChartTag, ChartResponse, 
    ChartTracksResponse, ChartTagsResponse
)

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
    "AlbumTopTagsResponse",
    
    # Track models
    "Track",
    "TrackListResponse",
    "TrackSearchResult", 
    "TrackSearchResponse",
    "TrackSimilarResponse",
    "TrackTopTagsResponse",
    "TrackScrobbleResponse",
    "TrackNowPlayingResponse",
    "TrackLoveResponse",
    "TrackUnloveResponse",
    "TrackAddTagsResponse",
    "TrackRemoveTagResponse",
    
    # User models
    "UserInfo",
    "Scrobble",
    "RecentTracksResponse",
    "UserTopArtist",
    "UserTopAlbum", 
    "UserTopTrack",
    "LovedTrack",
    "UserTopArtistsResponse",
    "UserTopAlbumsResponse",
    "UserTopTracksResponse",
    "UserLovedTracksResponse",
    
    # Tag models
    "Tag",
    "TaggedArtist",
    "TaggedAlbum",
    "TaggedTrack",
    "WeeklyChart",
    "TagTopArtistsResponse",
    "TagTopAlbumsResponse",
    "TagTopTracksResponse",
    "TagWeeklyChartListResponse",
    
    # Chart models
    "ChartArtist",
    "ChartTrack",
    "ChartTag",
    "ChartResponse",
    "ChartTracksResponse",
    "ChartTagsResponse",
]
