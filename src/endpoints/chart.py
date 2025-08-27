from typing import Dict, Any, Optional
from src.client import LastFmClient
from src.models import ChartResponse, ChartArtist


class ChartEndpoints:
    """
    Chart-related Last.fm API endpoints
    Provides clean interface for chart operations
    """
    
    def __init__(self, client: LastFmClient):
        self.client = client
    
    async def get_top_artists(
        self, 
        limit: int = 50,
        page: int = 1
    ) -> ChartResponse:
        """
        Get global top artists chart
        
        Args:
            limit: Number of results per page (max 1000)
            page: Page number to retrieve
        
        Returns:
            Global top artists with pagination
        """
        params = {
            "limit": str(min(limit, 1000)),
            "page": str(page)
        }
        
        raw_result = await self.client._make_request("chart.gettopartists", params)
        artists_data = raw_result.get("artists", {}).get("artist", [])
        
        if isinstance(artists_data, dict):  # Single artist
            artists_data = [artists_data]
        
        # Convert to models
        artists = [ChartArtist.from_lastfm_chart(artist) for artist in artists_data if isinstance(artist, dict)]
        
        # Extract pagination info
        attr = raw_result.get("artists", {}).get("@attr", {})
        
        return ChartResponse(
            page=int(attr.get("page", 1) or 1),
            per_page=int(attr.get("perPage", 50) or 50),
            total=int(attr.get("total", 0) or 0),
            total_pages=int(attr.get("totalPages", 1) or 1),
            artists=artists
        )
    
    async def get_top_tracks(
        self, 
        limit: int = 50,
        page: int = 1
    ) -> Dict[str, Any]:
        """
        Get global top tracks chart
        
        Args:
            limit: Number of results per page (max 1000)
            page: Page number to retrieve
        
        Returns:
            Global top tracks with pagination
        """
        params = {
            "limit": str(min(limit, 1000)),
            "page": str(page)
        }
        
        raw_result = await self.client._make_request("chart.gettoptracks", params)
        tracks_data = raw_result.get("tracks", {}).get("track", [])
        
        if isinstance(tracks_data, dict):  # Single track
            tracks_data = [tracks_data]
        
        # Extract pagination info
        attr = raw_result.get("tracks", {}).get("@attr", {})
        
        return {
            "page": int(attr.get("page", 1) or 1),
            "per_page": int(attr.get("perPage", 50) or 50),
            "total": int(attr.get("total", 0) or 0),
            "total_pages": int(attr.get("totalPages", 1) or 1),
            "tracks": [
                {
                    "name": track.get("name", ""),
                    "artist": track.get("artist", {}).get("name", "") if isinstance(track.get("artist"), dict) else str(track.get("artist", "")),
                    "mbid": track.get("mbid", ""),
                    "url": track.get("url", ""),
                    "playcount": int(track.get("playcount", 0) or 0),
                    "listeners": int(track.get("listeners", 0) or 0),
                    "rank": int(track.get("@attr", {}).get("rank", 0) or 0)
                }
                for track in tracks_data
                if isinstance(track, dict)
            ]
        }
    
    async def get_top_tags(
        self, 
        limit: int = 50,
        page: int = 1
    ) -> Dict[str, Any]:
        """
        Get global top tags chart
        
        Args:
            limit: Number of results per page (max 1000)
            page: Page number to retrieve
        
        Returns:
            Global top tags with pagination
        """
        params = {
            "limit": str(min(limit, 1000)),
            "page": str(page)
        }
        
        raw_result = await self.client._make_request("chart.gettoptags", params)
        tags_data = raw_result.get("tags", {}).get("tag", [])
        
        if isinstance(tags_data, dict):  # Single tag
            tags_data = [tags_data]
        
        # Extract pagination info
        attr = raw_result.get("tags", {}).get("@attr", {})
        
        return {
            "page": int(attr.get("page", 1) or 1),
            "per_page": int(attr.get("perPage", 50) or 50),
            "total": int(attr.get("total", 0) or 0),
            "total_pages": int(attr.get("totalPages", 1) or 1),
            "tags": [
                {
                    "name": tag.get("name", ""),
                    "url": tag.get("url", ""),
                    "reach": int(tag.get("reach", 0) or 0),
                    "taggings": int(tag.get("taggings", 0) or 0)
                }
                for tag in tags_data
                if isinstance(tag, dict)
            ]
        }
