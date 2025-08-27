from typing import Dict, Any, Optional
from src.client import LastFmClient
from src.models import Track, TrackSearchResponse, TrackSearchResult, TrackSimilarResponse, TrackTopTagsResponse


class TrackEndpoints:
    """
    Track-related Last.fm API endpoints
    Provides clean interface for track operations
    """
    
    def __init__(self, client: LastFmClient):
        self.client = client
    
    async def get_info(
        self, 
        artist: str, 
        track: str,
        mbid: Optional[str] = None,
        autocorrect: bool = True,
        username: Optional[str] = None
    ) -> Track:
        """
        Get detailed information about a track
        
        Args:
            artist: Artist name
            track: Track name
            mbid: MusicBrainz ID (optional, more accurate than name)
            autocorrect: Whether to correct misspelled names
            username: Username for personalized info (playcount, etc.)
        
        Returns:
            Detailed track information
        """
        params = {}
        
        # Primary identifier
        if mbid:
            params["mbid"] = mbid
        else:
            params["artist"] = artist
            params["track"] = track
        
        # Optional parameters
        if not autocorrect:
            params["autocorrect"] = "0"
        if username:
            params["username"] = username
        
        raw_result = await self.client._make_request("track.getinfo", params)
        return Track.from_lastfm_track(raw_result.get("track", {}))
    
    async def search(
        self, 
        track: str, 
        artist: Optional[str] = None,
        limit: int = 30, 
        page: int = 1
    ) -> TrackSearchResponse:
        """
        Search for tracks by name
        
        Args:
            track: Track name to search for
            artist: Optional artist name to narrow search
            limit: Number of results per page (max 1000)
            page: Page number to retrieve
        
        Returns:
            Search results with tracks list and metadata
        """
        params = {
            "track": track,
            "limit": str(min(limit, 1000)),  # Enforce API limit
            "page": str(page)
        }
        
        if artist:
            params["artist"] = artist
        
        raw_result = await self.client._make_request("track.search", params)
        results = raw_result.get("results", {})
        
        # Extract track matches
        track_matches = results.get("trackmatches", {}).get("track", [])
        if isinstance(track_matches, dict):  # Single result
            track_matches = [track_matches]
        
        # Convert to models
        tracks = [TrackSearchResult.from_lastfm_search(track) for track in track_matches if isinstance(track, dict)]
        
        return TrackSearchResponse(
            query=results.get("opensearch:Query", {}).get("#text", ""),
            total_results=int(results.get("opensearch:totalResults", 0) or 0),
            start_page=int(results.get("opensearch:startPage", 1) or 1),
            items_per_page=int(results.get("opensearch:itemsPerPage", 30) or 30),
            tracks=tracks
        )
    
    async def get_similar(
        self, 
        artist: str, 
        track: str,
        mbid: Optional[str] = None,
        autocorrect: bool = True,
        limit: int = 30
    ) -> TrackSimilarResponse:
        """
        Get similar tracks
        
        Args:
            artist: Artist name
            track: Track name
            mbid: MusicBrainz ID (optional)
            autocorrect: Whether to correct misspelled names
            limit: Number of similar tracks to return
        
        Returns:
            List of similar tracks
        """
        params = {
            "limit": str(limit)
        }
        
        if mbid:
            params["mbid"] = mbid
        else:
            params["artist"] = artist
            params["track"] = track
            
        if not autocorrect:
            params["autocorrect"] = "0"
        
        raw_result = await self.client._make_request("track.getsimilar", params)
        similar_tracks = raw_result.get("similartracks", {}).get("track", [])
        
        if isinstance(similar_tracks, dict):  # Single track
            similar_tracks = [similar_tracks]
        
        return TrackSimilarResponse(
            artist=artist,
            track=track,
            similar=[
                {
                    "name": track.get("name", ""),
                    "artist": track.get("artist", {}).get("name", "") if isinstance(track.get("artist"), dict) else str(track.get("artist", "")),
                    "mbid": track.get("mbid", ""),
                    "match": float(track.get("match", 0)),
                    "url": track.get("url", ""),
                    "duration": int(track.get("duration", 0) or 0)
                }
                for track in similar_tracks
                if isinstance(track, dict)
            ]
        )
    
    async def get_top_tags(
        self, 
        artist: str, 
        track: str,
        mbid: Optional[str] = None,
        autocorrect: bool = True
    ) -> TrackTopTagsResponse:
        """
        Get top tags for a track
        
        Args:
            artist: Artist name
            track: Track name
            mbid: MusicBrainz ID (optional)
            autocorrect: Whether to correct misspelled names
        
        Returns:
            List of top tags for the track
        """
        params = {}
        
        if mbid:
            params["mbid"] = mbid
        else:
            params["artist"] = artist
            params["track"] = track
            
        if not autocorrect:
            params["autocorrect"] = "0"
        
        raw_result = await self.client._make_request("track.gettoptags", params)
        tags_data = raw_result.get("toptags", {}).get("tag", [])
        
        if isinstance(tags_data, dict):  # Single tag
            tags_data = [tags_data]
        
        return TrackTopTagsResponse(
            artist=artist,
            track=track,
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
    
    async def scrobble(
        self,
        artist: str,
        track: str,
        timestamp: int,
        album: Optional[str] = None,
        album_artist: Optional[str] = None,
        duration: Optional[int] = None,
        stream_id: Optional[str] = None,
        chosen_by_user: bool = True,
        context: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Scrobble a track to user's Last.fm profile
        Requires authentication (signed request)
        
        Args:
            artist: Artist name
            track: Track name
            timestamp: Unix timestamp when track was played
            album: Album name (optional)
            album_artist: Album artist if different from track artist (optional)
            duration: Track duration in seconds (optional)
            stream_id: Stream ID for streaming services (optional)
            chosen_by_user: Whether user chose to play this track (optional)
            context: Additional context (optional)
        
        Returns:
            Scrobble confirmation
        """
        params = {
            "artist": artist,
            "track": track,
            "timestamp": str(timestamp)
        }
        
        # Optional parameters
        if album:
            params["album"] = album
        if album_artist:
            params["albumArtist"] = album_artist
        if duration:
            params["duration"] = str(duration)
        if stream_id:
            params["streamId"] = stream_id
        if not chosen_by_user:
            params["chosenByUser"] = "0"
        if context:
            params["context"] = context
        
        raw_result = await self.client._make_request("track.scrobble", params, signed=True, http_method="POST")
        
        # Process scrobble response
        scrobbles = raw_result.get("scrobbles", {})
        return {
            "accepted": int(scrobbles.get("@attr", {}).get("accepted", 0)),
            "ignored": int(scrobbles.get("@attr", {}).get("ignored", 0)),
            "scrobble": scrobbles.get("scrobble", {})
        }
    
    async def love(
        self,
        artist: str,
        track: str,
        session_key: str
    ) -> Dict[str, Any]:
        """
        Love a track for the authenticated user
        Requires authentication (session key)
        
        Args:
            artist: Artist name
            track: Track name
            session_key: User's session key from authentication
        
        Returns:
            Confirmation of love action
        """
        params = {
            "artist": artist,
            "track": track,
            "sk": session_key
        }
        
        raw_result = await self.client._make_request("track.love", params, signed=True, http_method="POST")
        return {
            "status": "loved",
            "artist": artist,
            "track": track
        }
    
    async def unlove(
        self,
        artist: str,
        track: str,
        session_key: str
    ) -> Dict[str, Any]:
        """
        Remove love from a track for the authenticated user
        Requires authentication (session key)
        
        Args:
            artist: Artist name
            track: Track name
            session_key: User's session key from authentication
        
        Returns:
            Confirmation of unlove action
        """
        params = {
            "artist": artist,
            "track": track,
            "sk": session_key
        }
        
        raw_result = await self.client._make_request("track.unlove", params, signed=True, http_method="POST")
        return {
            "status": "unloved",
            "artist": artist,
            "track": track
        }
    
    async def update_now_playing(
        self,
        artist: str,
        track: str,
        session_key: str,
        album: Optional[str] = None,
        album_artist: Optional[str] = None,
        duration: Optional[int] = None,
        track_number: Optional[int] = None,
        mbid: Optional[str] = None,
        context: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Update the user's "now playing" status
        Requires authentication (session key)
        
        Args:
            artist: Artist name
            track: Track name
            session_key: User's session key from authentication
            album: Album name (optional)
            album_artist: Album artist if different from track artist (optional)
            duration: Track duration in seconds (optional)
            track_number: Track number on album (optional)
            mbid: MusicBrainz ID (optional)
            context: Additional context (optional)
        
        Returns:
            Confirmation of now playing update
        """
        params = {
            "artist": artist,
            "track": track,
            "sk": session_key
        }
        
        # Optional parameters
        if album:
            params["album"] = album
        if album_artist:
            params["albumArtist"] = album_artist
        if duration:
            params["duration"] = str(duration)
        if track_number:
            params["trackNumber"] = str(track_number)
        if mbid:
            params["mbid"] = mbid
        if context:
            params["context"] = context
        
        raw_result = await self.client._make_request("track.updateNowPlaying", params, signed=True, http_method="POST")
        
        # Process now playing response
        now_playing = raw_result.get("nowplaying", {})
        return {
            "status": "now_playing_updated",
            "artist": now_playing.get("artist", {}).get("#text", artist),
            "track": now_playing.get("track", {}).get("#text", track),
            "album": now_playing.get("album", {}).get("#text", album) if album else None,
            "corrected_artist": now_playing.get("artist", {}).get("corrected", "0") == "1",
            "corrected_track": now_playing.get("track", {}).get("corrected", "0") == "1"
        }
    
    async def add_tags(
        self,
        artist: str,
        track: str,
        tags: str,
        session_key: str
    ) -> Dict[str, Any]:
        """
        Add tags to a track
        Requires authentication (session key)
        
        Args:
            artist: Artist name
            track: Track name
            tags: Comma-separated list of tags (max 10)
            session_key: User's session key from authentication
        
        Returns:
            Confirmation of tag addition
        """
        params = {
            "artist": artist,
            "track": track,
            "tags": tags,
            "sk": session_key
        }
        
        raw_result = await self.client._make_request("track.addTags", params, signed=True, http_method="POST")
        return {
            "status": "tags_added",
            "artist": artist,
            "track": track,
            "tags": tags.split(",")
        }
    
    async def remove_tag(
        self,
        artist: str,
        track: str,
        tag: str,
        session_key: str
    ) -> Dict[str, Any]:
        """
        Remove a tag from a track
        Requires authentication (session key)
        
        Args:
            artist: Artist name
            track: Track name
            tag: Tag to remove
            session_key: User's session key from authentication
        
        Returns:
            Confirmation of tag removal
        """
        params = {
            "artist": artist,
            "track": track,
            "tag": tag,
            "sk": session_key
        }
        
        raw_result = await self.client._make_request("track.removeTag", params, signed=True, http_method="POST")
        return {
            "status": "tag_removed",
            "artist": artist,
            "track": track,
            "tag": tag
        }
