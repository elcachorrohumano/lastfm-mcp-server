from typing import Dict, Any, Optional
from src.client import LastFmClient
from src.models import Tag, TagTopArtistsResponse, TaggedArtist


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
    ) -> Dict[str, Any]:
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
        top_albums = raw_result.get("topalbums", {})
        albums_data = top_albums.get("album", [])
        
        if isinstance(albums_data, dict):  # Single album
            albums_data = [albums_data]
        
        # Extract pagination info
        attr = top_albums.get("@attr", {})
        
        return {
            "tag": attr.get("tag", tag),
            "total": int(attr.get("total", 0) or 0),
            "page": int(attr.get("page", 1) or 1),
            "per_page": int(attr.get("perPage", 50) or 50),
            "albums": [
                {
                    "name": album.get("name", ""),
                    "artist": album.get("artist", {}).get("name", "") if isinstance(album.get("artist"), dict) else str(album.get("artist", "")),
                    "mbid": album.get("mbid", ""),
                    "url": album.get("url", ""),
                    "rank": int(album.get("@attr", {}).get("rank", 0) or 0)
                }
                for album in albums_data
                if isinstance(album, dict)
            ]
        }
    
    async def get_top_tracks(
        self, 
        tag: str,
        limit: int = 50,
        page: int = 1
    ) -> Dict[str, Any]:
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
        top_tracks = raw_result.get("toptracks", {})
        tracks_data = top_tracks.get("track", [])
        
        if isinstance(tracks_data, dict):  # Single track
            tracks_data = [tracks_data]
        
        # Extract pagination info
        attr = top_tracks.get("@attr", {})
        
        return {
            "tag": attr.get("tag", tag),
            "total": int(attr.get("total", 0) or 0),
            "page": int(attr.get("page", 1) or 1),
            "per_page": int(attr.get("perPage", 50) or 50),
            "tracks": [
                {
                    "name": track.get("name", ""),
                    "artist": track.get("artist", {}).get("name", "") if isinstance(track.get("artist"), dict) else str(track.get("artist", "")),
                    "mbid": track.get("mbid", ""),
                    "url": track.get("url", ""),
                    "rank": int(track.get("@attr", {}).get("rank", 0) or 0),
                    "duration": int(track.get("duration", 0) or 0)
                }
                for track in tracks_data
                if isinstance(track, dict)
            ]
        }
    
    async def get_weekly_chart_list(
        self, 
        tag: str
    ) -> Dict[str, Any]:
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
        
        return {
            "tag": tag,
            "charts": [
                {
                    "from": chart.get("from", ""),
                    "to": chart.get("to", ""),
                    "text": chart.get("#text", "")
                }
                for chart in charts_data
                if isinstance(chart, dict)
            ]
        }
