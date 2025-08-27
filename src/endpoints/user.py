from typing import Dict, Any, Optional
from src.client import LastFmClient
from src.models import (
    UserInfo, RecentTracksResponse, Scrobble,
    UserTopArtistsResponse, UserTopAlbumsResponse, UserTopTracksResponse, UserLovedTracksResponse,
    UserTopArtist, UserTopAlbum, UserTopTrack, LovedTrack, LastFmDate
)


class UserEndpoints:
    """
    User-related Last.fm API endpoints
    Provides clean interface for user operations
    """
    
    def __init__(self, client: LastFmClient):
        self.client = client
    
    async def get_info(
        self, 
        user: str
    ) -> UserInfo:
        """
        Get detailed information about a user
        
        Args:
            user: Username to get info for
        
        Returns:
            User profile information
        """
        params = {
            "user": user
        }
        
        raw_result = await self.client._make_request("user.getinfo", params)
        return UserInfo.from_lastfm_user(raw_result.get("user", {}))
    
    async def get_recent_tracks(
        self, 
        user: str,
        limit: int = 50,
        page: int = 1,
        from_timestamp: Optional[int] = None,
        to_timestamp: Optional[int] = None,
        extended: bool = False
    ) -> RecentTracksResponse:
        """
        Get user's recent tracks (scrobbles)
        
        Args:
            user: Username
            limit: Number of results per page (max 200)
            page: Page number to retrieve
            from_timestamp: Unix timestamp to start from (optional)
            to_timestamp: Unix timestamp to end at (optional)
            extended: Include extended data (optional)
        
        Returns:
            Recent tracks with pagination info
        """
        params = {
            "user": user,
            "limit": str(min(limit, 200)),  # Enforce API limit
            "page": str(page)
        }
        
        if from_timestamp:
            params["from"] = str(from_timestamp)
        if to_timestamp:
            params["to"] = str(to_timestamp)
        if extended:
            params["extended"] = "1"
        
        raw_result = await self.client._make_request("user.getrecenttracks", params)
        recent_tracks = raw_result.get("recenttracks", {})
        tracks_data = recent_tracks.get("track", [])
        
        if isinstance(tracks_data, dict):  # Single track
            tracks_data = [tracks_data]
        
        # Convert to models
        tracks = [Scrobble.from_lastfm_scrobble(track) for track in tracks_data if isinstance(track, dict)]
        
        # Extract pagination info
        attr = recent_tracks.get("@attr", {})
        
        return RecentTracksResponse(
            user=attr.get("user", user),
            total=int(attr.get("total", 0) or 0),
            page=int(attr.get("page", 1) or 1),
            per_page=int(attr.get("perPage", 50) or 50),
            total_pages=int(attr.get("totalPages", 1) or 1),
            tracks=tracks
        )
    
    async def get_top_artists(
        self, 
        user: str,
        period: str = "overall",
        limit: int = 50,
        page: int = 1
    ) -> UserTopArtistsResponse:
        """
        Get user's top artists
        
        Args:
            user: Username
            period: Time period (7day, 1month, 3month, 6month, 12month, overall)
            limit: Number of results per page (max 1000)
            page: Page number to retrieve
        
        Returns:
            Top artists with stats
        """
        params = {
            "user": user,
            "period": period,
            "limit": str(min(limit, 1000)),
            "page": str(page)
        }
        
        raw_result = await self.client._make_request("user.gettopartists", params)
        top_artists = raw_result.get("topartists", {})
        artists_data = top_artists.get("artist", [])
        
        if isinstance(artists_data, dict):  # Single artist
            artists_data = [artists_data]
        
        # Extract pagination info
        attr = top_artists.get("@attr", {})
        
        return UserTopArtistsResponse(
            user=attr.get("user", user),
            period=period,
            total=int(attr.get("total", 0) or 0),
            page=int(attr.get("page", 1) or 1),
            per_page=int(attr.get("perPage", 50) or 50),
            total_pages=int(attr.get("totalPages", 1) or 1),
            artists=[
                UserTopArtist(
                    name=artist.get("name", ""),
                    mbid=artist.get("mbid", ""),
                    url=artist.get("url", ""),
                    playcount=int(artist.get("playcount", 0) or 0),
                    rank=int(artist.get("@attr", {}).get("rank", 0) or 0)
                )
                for artist in artists_data
                if isinstance(artist, dict)
            ]
        )
    
    async def get_top_albums(
        self, 
        user: str,
        period: str = "overall",
        limit: int = 50,
        page: int = 1
    ) -> UserTopAlbumsResponse:
        """
        Get user's top albums
        
        Args:
            user: Username
            period: Time period (7day, 1month, 3month, 6month, 12month, overall)
            limit: Number of results per page (max 1000)
            page: Page number to retrieve
        
        Returns:
            Top albums with stats
        """
        params = {
            "user": user,
            "period": period,
            "limit": str(min(limit, 1000)),
            "page": str(page)
        }
        
        raw_result = await self.client._make_request("user.gettopalbums", params)
        top_albums = raw_result.get("topalbums", {})
        albums_data = top_albums.get("album", [])
        
        if isinstance(albums_data, dict):  # Single album
            albums_data = [albums_data]
        
        # Extract pagination info
        attr = top_albums.get("@attr", {})
        
        return UserTopAlbumsResponse(
            user=attr.get("user", user),
            period=period,
            total=int(attr.get("total", 0) or 0),
            page=int(attr.get("page", 1) or 1),
            per_page=int(attr.get("perPage", 50) or 50),
            total_pages=int(attr.get("totalPages", 1) or 1),
            albums=[
                UserTopAlbum(
                    name=album.get("name", ""),
                    artist=album.get("artist", {}).get("name", "") if isinstance(album.get("artist"), dict) else str(album.get("artist", "")),
                    mbid=album.get("mbid", ""),
                    url=album.get("url", ""),
                    playcount=int(album.get("playcount", 0) or 0),
                    rank=int(album.get("@attr", {}).get("rank", 0) or 0)
                )
                for album in albums_data
                if isinstance(album, dict)
            ]
        )
    
    async def get_top_tracks(
        self, 
        user: str,
        period: str = "overall",
        limit: int = 50,
        page: int = 1
    ) -> UserTopTracksResponse:
        """
        Get user's top tracks
        
        Args:
            user: Username
            period: Time period (7day, 1month, 3month, 6month, 12month, overall)
            limit: Number of results per page (max 1000)
            page: Page number to retrieve
        
        Returns:
            Top tracks with stats
        """
        params = {
            "user": user,
            "period": period,
            "limit": str(min(limit, 1000)),
            "page": str(page)
        }
        
        raw_result = await self.client._make_request("user.gettoptracks", params)
        top_tracks = raw_result.get("toptracks", {})
        tracks_data = top_tracks.get("track", [])
        
        if isinstance(tracks_data, dict):  # Single track
            tracks_data = [tracks_data]
        
        # Extract pagination info
        attr = top_tracks.get("@attr", {})
        
        return UserTopTracksResponse(
            user=attr.get("user", user),
            period=period,
            total=int(attr.get("total", 0) or 0),
            page=int(attr.get("page", 1) or 1),
            per_page=int(attr.get("perPage", 50) or 50),
            total_pages=int(attr.get("totalPages", 1) or 1),
            tracks=[
                UserTopTrack(
                    name=track.get("name", ""),
                    artist=track.get("artist", {}).get("name", "") if isinstance(track.get("artist"), dict) else str(track.get("artist", "")),
                    mbid=track.get("mbid", ""),
                    url=track.get("url", ""),
                    playcount=int(track.get("playcount", 0) or 0),
                    rank=int(track.get("@attr", {}).get("rank", 0) or 0)
                )
                for track in tracks_data
                if isinstance(track, dict)
            ]
        )
    
    async def get_loved_tracks(
        self, 
        user: str,
        limit: int = 50,
        page: int = 1
    ) -> UserLovedTracksResponse:
        """
        Get user's loved tracks
        
        Args:
            user: Username
            limit: Number of results per page (max 1000)
            page: Page number to retrieve
        
        Returns:
            Loved tracks list
        """
        params = {
            "user": user,
            "limit": str(min(limit, 1000)),
            "page": str(page)
        }
        
        raw_result = await self.client._make_request("user.getlovedtracks", params)
        loved_tracks = raw_result.get("lovedtracks", {})
        tracks_data = loved_tracks.get("track", [])
        
        if isinstance(tracks_data, dict):  # Single track
            tracks_data = [tracks_data]
        
        # Extract pagination info
        attr = loved_tracks.get("@attr", {})
        
        return UserLovedTracksResponse(
            user=attr.get("user", user),
            total=int(attr.get("total", 0) or 0),
            page=int(attr.get("page", 1) or 1),
            per_page=int(attr.get("perPage", 50) or 50),
            total_pages=int(attr.get("totalPages", 1) or 1),
            tracks=[
                LovedTrack(
                    name=track.get("name", ""),
                    artist=track.get("artist", {}).get("name", "") if isinstance(track.get("artist"), dict) else str(track.get("artist", "")),
                    mbid=track.get("mbid", ""),
                    url=track.get("url", ""),
                    date=LastFmDate.from_lastfm_date(track.get("date", {}))
                )
                for track in tracks_data
                if isinstance(track, dict)
            ]
        )
