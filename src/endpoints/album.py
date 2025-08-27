from typing import Dict, Any, Optional
from src.client import LastFmClient
from src.models import Album, AlbumSearchResponse, AlbumSearchResult, AlbumTopTagsResponse


class AlbumEndpoints:
    """
    Album-related Last.fm API endpoints
    Provides clean interface for album operations
    """
    
    def __init__(self, client: LastFmClient):
        self.client = client
    
    async def get_info(
        self, 
        artist: str, 
        album: str,
        mbid: Optional[str] = None,
        autocorrect: bool = True,
        username: Optional[str] = None,
        lang: Optional[str] = None
    ) -> Album:
        """
        Get detailed information about an album
        
        Args:
            artist: Artist name
            album: Album name
            mbid: MusicBrainz ID (optional, more accurate than name)
            autocorrect: Whether to correct misspelled names
            username: Username for personalized info (playcount, etc.)
            lang: Language code for wiki content
        
        Returns:
            Detailed album information
        """
        params = {}
        
        # Primary identifier
        if mbid:
            params["mbid"] = mbid
        else:
            params["artist"] = artist
            params["album"] = album
        
        # Optional parameters
        if not autocorrect:
            params["autocorrect"] = "0"
        if username:
            params["username"] = username
        if lang:
            params["lang"] = lang
        
        raw_result = await self.client._make_request("album.getinfo", params)
        return Album.from_lastfm_album(raw_result.get("album", {}))
    
    async def search(
        self, 
        album: str, 
        limit: int = 30, 
        page: int = 1
    ) -> AlbumSearchResponse:
        """
        Search for albums by name
        
        Args:
            album: Album name to search for
            limit: Number of results per page (max 1000)
            page: Page number to retrieve
        
        Returns:
            Search results with albums list and metadata
        """
        params = {
            "album": album,
            "limit": str(min(limit, 1000)),  # Enforce API limit
            "page": str(page)
        }
        
        raw_result = await self.client._make_request("album.search", params)
        results = raw_result.get("results", {})
        
        # Extract album matches
        album_matches = results.get("albummatches", {}).get("album", [])
        if isinstance(album_matches, dict):  # Single result
            album_matches = [album_matches]
        
        # Convert to models
        albums = [AlbumSearchResult.from_lastfm_search(album) for album in album_matches if isinstance(album, dict)]
        
        return AlbumSearchResponse(
            query=results.get("opensearch:Query", {}).get("#text", ""),
            total_results=int(results.get("opensearch:totalResults", 0) or 0),
            start_page=int(results.get("opensearch:startPage", 1) or 1),
            items_per_page=int(results.get("opensearch:itemsPerPage", 30) or 30),
            albums=albums
        )
    
    async def get_top_tags(
        self, 
        artist: str, 
        album: str,
        mbid: Optional[str] = None,
        autocorrect: bool = True
    ) -> AlbumTopTagsResponse:
        """
        Get top tags for an album
        
        Args:
            artist: Artist name
            album: Album name
            mbid: MusicBrainz ID (optional)
            autocorrect: Whether to correct misspelled names
        
        Returns:
            List of top tags for the album
        """
        params = {}
        
        if mbid:
            params["mbid"] = mbid
        else:
            params["artist"] = artist
            params["album"] = album
            
        if not autocorrect:
            params["autocorrect"] = "0"
        
        raw_result = await self.client._make_request("album.gettoptags", params)
        tags_data = raw_result.get("toptags", {}).get("tag", [])
        
        if isinstance(tags_data, dict):  # Single tag
            tags_data = [tags_data]
        
        return AlbumTopTagsResponse(
            artist=artist,
            album=album,
            tags=[
                {
                    "name": tag.get("name", ""),
                    "count": int(tag.get("count", 0) or 0),
                    "url": tag.get("url", "")
                }
                for tag in tags_data
                if isinstance(tag, dict)
            ]
        )
