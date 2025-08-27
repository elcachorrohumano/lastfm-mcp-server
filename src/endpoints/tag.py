from typing import Dict, Any, Optional
from src.client import LastFmClient
from src.models import (
    Tag, TagTopArtistsResponse, TaggedArtist,
    TagTopAlbumsResponse, TagTopTracksResponse, TagWeeklyChartListResponse,
    TaggedAlbum, TaggedTrack, WeeklyChart
)


class TagEndpoints:
    """
    Tag-related Last.fm API endpoints
    Provides clean interface for tag operations
    """
    
    def __init__(self, client: LastFmClient):
        self.client = client
    
    async def get_info(
        self, 
        tag: str,
        lang: Optional[str] = None
    ) -> Tag:
        """
        Get detailed information about a tag
        
        Args:
            tag: Tag name
            lang: Language code for wiki content (optional)
        
        Returns:
            Detailed tag information
        """
        params = {
            "tag": tag
        }
        
        if lang:
            params["lang"] = lang
        
        raw_result = await self.client._make_request("tag.getinfo", params)
        return Tag.from_lastfm_tag(raw_result.get("tag", {}))
    
    async def get_top_artists(
        self, 
        tag: str,
        limit: int = 50,
        page: int = 1
    ) -> TagTopArtistsResponse:
        """
        Get top artists for a tag
        
        Args:
            tag: Tag name
            limit: Number of results per page (max 1000)
            page: Page number to retrieve
        
        Returns:
            Top artists for the tag with pagination
        """
        params = {
            "tag": tag,
            "limit": str(min(limit, 1000)),
            "page": str(page)
        }
        
        raw_result = await self.client._make_request("tag.gettopartists", params)
        top_artists = raw_result.get("topartists", {})
        artists_data = top_artists.get("artist", [])
        
        if isinstance(artists_data, dict):  # Single artist
            artists_data = [artists_data]
        
        # Convert to models
        artists = [TaggedArtist.from_lastfm_tagged(artist) for artist in artists_data if isinstance(artist, dict)]
        
        # Extract pagination info
        attr = top_artists.get("@attr", {})
        
        return TagTopArtistsResponse(
            tag=attr.get("tag", tag),
            total=int(attr.get("total", 0) or 0),
            page=int(attr.get("page", 1) or 1),
            per_page=int(attr.get("perPage", 50) or 50),
            artists=artists
        )
    
    async def get_top_albums(
        self, 
        tag: str,
        limit: int = 50,
        page: int = 1
    ) -> TagTopAlbumsResponse:
        """
        Get top albums for a tag
        
        Args:
            tag: Tag name
            limit: Number of results per page (max 1000)
            page: Page number to retrieve
        
        Returns:
            Top albums for the tag
        """
        params = {
            "tag": tag,
            "limit": str(min(limit, 1000)),
            "page": str(page)
        }
        
        raw_result = await self.client._make_request("tag.gettopalbums", params)
        # Handle both old "topalbums" and new "albums" response structure
        top_albums = raw_result.get("topalbums", raw_result.get("albums", {}))
        albums_data = top_albums.get("album", [])
        
        if isinstance(albums_data, dict):  # Single album
            albums_data = [albums_data]
        
        # Convert to models
        albums = [TaggedAlbum.from_lastfm_tagged(album) for album in albums_data if isinstance(album, dict)]
        
        # Extract pagination info
        attr = top_albums.get("@attr", {})
        
        return TagTopAlbumsResponse(
            tag=attr.get("tag", tag),
            total=int(attr.get("total", 0) or 0),
            page=int(attr.get("page", 1) or 1),
            per_page=int(attr.get("perPage", 50) or 50),
            albums=albums
        )
    
    async def get_top_tracks(
        self, 
        tag: str,
        limit: int = 50,
        page: int = 1
    ) -> TagTopTracksResponse:
        """
        Get top tracks for a tag
        
        Args:
            tag: Tag name
            limit: Number of results per page (max 1000)
            page: Page number to retrieve
        
        Returns:
            Top tracks for the tag
        """
        params = {
            "tag": tag,
            "limit": str(min(limit, 1000)),
            "page": str(page)
        }
        
        raw_result = await self.client._make_request("tag.gettoptracks", params)
        # Handle both old "toptracks" and new "tracks" response structure
        top_tracks = raw_result.get("toptracks", raw_result.get("tracks", {}))
        tracks_data = top_tracks.get("track", [])
        
        if isinstance(tracks_data, dict):  # Single track
            tracks_data = [tracks_data]
        
        # Convert to models
        tracks = [TaggedTrack.from_lastfm_tagged(track) for track in tracks_data if isinstance(track, dict)]
        
        # Extract pagination info
        attr = top_tracks.get("@attr", {})
        
        return TagTopTracksResponse(
            tag=attr.get("tag", tag),
            total=int(attr.get("total", 0) or 0),
            page=int(attr.get("page", 1) or 1),
            per_page=int(attr.get("perPage", 50) or 50),
            tracks=tracks
        )
    
    async def get_weekly_chart_list(
        self, 
        tag: str
    ) -> TagWeeklyChartListResponse:
        """
        Get list of available weekly charts for a tag
        
        Args:
            tag: Tag name
        
        Returns:
            List of available chart periods
        """
        params = {
            "tag": tag
        }
        
        raw_result = await self.client._make_request("tag.getweeklychartlist", params)
        weekly_chart_list = raw_result.get("weeklychartlist", {})
        charts_data = weekly_chart_list.get("chart", [])
        
        if isinstance(charts_data, dict):  # Single chart
            charts_data = [charts_data]
        
        # Convert to models
        charts = [WeeklyChart.from_lastfm_weekly_chart(chart) for chart in charts_data if isinstance(chart, dict)]
        
        return TagWeeklyChartListResponse(
            tag=tag,
            charts=charts
        )
