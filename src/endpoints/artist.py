from typing import Dict, Any, Optional, List
from src.client import LastFmClient
from src.models import (
    ArtistInfo,     
    ArtistSearchResponse, 
    AlbumListResponse, 
    TrackListResponse, 
    ArtistSearchResult, 
    Album, 
    Track
)


class ArtistEndpoints:
    """
    Artist-related Last.fm API endpoints
    Provides clean interface for artist operations
    """
    
    def __init__(self, client: LastFmClient):
        self.client = client
    
    async def get_info(
        self, 
        artist: Optional[str] = None, 
        mbid: Optional[str] = None,
        lang: Optional[str] = None,
        autocorrect: bool = True,
        username: Optional[str] = None
    ) -> ArtistInfo:
        """
        Get detailed information about an artist
        
        Args:
            artist: Artist name (optional if mbid is provided)
            mbid: MusicBrainz ID (optional, more accurate than name)
            lang: Language code for biography (e.g., 'en', 'es')
            autocorrect: Whether to correct misspelled artist names
            username: Username for personalized info (playcount, etc.)
        
        Returns:
            Processed artist information
        """
        params = {}
        
        # Primary identifier - either mbid or artist name must be provided
        if mbid:
            params["mbid"] = mbid
        elif artist:
            params["artist"] = artist
        else:
            raise ValueError("Either 'artist' name or 'mbid' must be provided")
        
        # Optional parameters
        if lang:
            params["lang"] = lang
        if not autocorrect:
            params["autocorrect"] = "0"
        if username:
            params["username"] = username
        
        raw_result = await self.client._make_request("artist.getinfo", params)
        return ArtistInfo.from_lastfm_artist(raw_result.get("artist", {}))
    
    async def search(
        self, 
        artist: str, 
        limit: int = 30, 
        page: int = 1
    ) -> ArtistSearchResponse:
        """
        Search for artists by name
        
        Args:
            artist: Artist name to search for
            limit: Number of results per page (max 1000)
            page: Page number to retrieve
        
        Returns:
            Search results with artists list and metadata
        """
        params = {
            "artist": artist,
            "limit": str(min(limit, 1000)),  # Enforce API limit
            "page": str(page)
        }
        
        raw_result = await self.client._make_request("artist.search", params)
        results = raw_result.get("results", {})
        
        # Extract artist matches
        artist_matches = results.get("artistmatches", {}).get("artist", [])
        if isinstance(artist_matches, dict):  # Single result
            artist_matches = [artist_matches]
        
        # Convert to models
        artists = [ArtistSearchResult.from_lastfm_search(artist) for artist in artist_matches if isinstance(artist, dict)]
        
        return ArtistSearchResponse(
            query=results.get("opensearch:Query", {}).get("#text", ""),
            total_results=int(results.get("opensearch:totalResults", 0) or 0),
            start_page=int(results.get("opensearch:startPage", 1) or 1),
            items_per_page=int(results.get("opensearch:itemsPerPage", 30) or 30),
            artists=artists
        )
    
    async def get_top_albums(
        self, 
        artist: str, 
        mbid: Optional[str] = None,
        autocorrect: bool = True,
        limit: int = 50,
        page: int = 1
    ) -> AlbumListResponse:
        """
        Get top albums for an artist
        
        Args:
            artist: Artist name
            mbid: MusicBrainz ID (optional)
            autocorrect: Whether to correct misspelled artist names
            limit: Number of results per page (max 1000)
            page: Page number to retrieve
        
        Returns:
            List of top albums with metadata
        """
        params = {
            "limit": str(min(limit, 1000)),
            "page": str(page)
        }
        
        if mbid:
            params["mbid"] = mbid
        else:
            params["artist"] = artist
            
        if not autocorrect:
            params["autocorrect"] = "0"
        
        raw_result = await self.client._make_request("artist.gettopalbums", params)
        top_albums = raw_result.get("topalbums", {})
        albums_data = top_albums.get("album", [])
        
        if isinstance(albums_data, dict):  # Single result
            albums_data = [albums_data]
        
        # Convert to models
        albums = [Album.from_lastfm_album(album) for album in albums_data if isinstance(album, dict)]
        
        return AlbumListResponse(
            artist=top_albums.get("@attr", {}).get("artist", ""),
            total=int(top_albums.get("@attr", {}).get("total", 0) or 0),
            page=int(top_albums.get("@attr", {}).get("page", 1) or 1),
            per_page=int(top_albums.get("@attr", {}).get("perPage", 50) or 50),
            albums=albums
        )
    
    async def get_top_tracks(
        self, 
        artist: str, 
        mbid: Optional[str] = None,
        autocorrect: bool = True,
        limit: int = 50,
        page: int = 1
    ) -> TrackListResponse:
        """
        Get top tracks for an artist
        
        Args:
            artist: Artist name
            mbid: MusicBrainz ID (optional)
            autocorrect: Whether to correct misspelled artist names
            limit: Number of results per page (max 1000)
            page: Page number to retrieve
        
        Returns:
            List of top tracks with metadata
        """
        params = {
            "limit": str(min(limit, 1000)),
            "page": str(page)
        }
        
        if mbid:
            params["mbid"] = mbid
        else:
            params["artist"] = artist
            
        if not autocorrect:
            params["autocorrect"] = "0"
        
        raw_result = await self.client._make_request("artist.gettoptracks", params)
        top_tracks = raw_result.get("toptracks", {})
        tracks_data = top_tracks.get("track", [])
        
        if isinstance(tracks_data, dict):  # Single result
            tracks_data = [tracks_data]
        
        # Convert to models
        tracks = [Track.from_lastfm_track(track) for track in tracks_data if isinstance(track, dict)]
        
        return TrackListResponse(
            artist=top_tracks.get("@attr", {}).get("artist", ""),
            total=int(top_tracks.get("@attr", {}).get("total", 0) or 0),
            page=int(top_tracks.get("@attr", {}).get("page", 1) or 1),
            per_page=int(top_tracks.get("@attr", {}).get("perPage", 50) or 50),
            tracks=tracks
        )

