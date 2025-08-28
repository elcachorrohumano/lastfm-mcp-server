#!/usr/bin/env python3
"""
Last.fm MCP Server
Provides Last.fm music data and discovery tools for AI assistants
"""

import asyncio
import logging
import os
import sys
import time
from typing import Optional

from mcp.server import FastMCP
from dotenv import load_dotenv

from src.client import LastFmClient
from src.endpoints.artist import ArtistEndpoints
from src.endpoints.album import AlbumEndpoints
from src.endpoints.track import TrackEndpoints
from src.endpoints.user import UserEndpoints
from src.endpoints.tag import TagEndpoints
from src.endpoints.chart import ChartEndpoints
from src.endpoints.auth import AuthEndpoints

# Configure simple logging
logging.basicConfig(
    level=logging.INFO,
    format='%(levelname)s: %(message)s',
    stream=sys.stderr
)
logger = logging.getLogger(__name__)

# Load environment variables
logger.info("Reading .env file...")
load_dotenv()

api_key = os.getenv("LASTFM_API_KEY")
if not api_key:
    logger.error("LASTFM_API_KEY not found in .env file")
    sys.exit(1)
shared_secret = os.getenv("LASTFM_SHARED_SECRET")
if not shared_secret:
    logger.error("LASTFM_SHARED_SECRET not found in .env file")
    sys.exit(1)

mcp = FastMCP("Last.fm Music Discovery")

client = LastFmClient()
artist_api = ArtistEndpoints(client)
album_api = AlbumEndpoints(client)
track_api = TrackEndpoints(client)
user_api = UserEndpoints(client)
tag_api = TagEndpoints(client)
chart_api = ChartEndpoints(client)
auth_api = AuthEndpoints(client)
logger.info("Last.fm MCP Server initialized successfully")

# ======= Artist Tools =======

@mcp.tool()
async def search_artists(
    query: str,
    limit: int = 10,
    page: int = 1
) -> str:
    """
    Search for artists on Last.fm by name
    
    Args:
        query: Artist name or search query
        limit: Maximum number of results to return (1-50, default: 10)
        page: Page number to retrieve (default: 1)
    Returns:
        Formatted list of matching artists with their stats
    """
    try:
        limit = max(1, min(limit, 50))
        result = await artist_api.search(query, limit=limit)
        return result.to_string()
        
    except Exception as e:
        return f"Error searching artists: {str(e)}"

@mcp.tool()
async def get_artist_info(
    artist: Optional[str] = None,
    mbid: Optional[str] = None,
    lang: Optional[str] = None,
    autocorrect: bool = True,
    username: Optional[str] = None
) -> str:
    """
    Get detailed information about an artist by name or MBID
    
    Args:
        artist: Artist name to search for (optional if mbid is provided)
        mbid: Optional MBID (MusicBrainz ID) of the artist (optional if artist is provided)
        lang: Language code for the artist info (as an ISO 639 alpha-2 code)
        autocorrect: Whether to use autocorrection for the artist name
        username: Username for personalized info (playcount, etc.)
    
    Returns:
        Formatted detailed artist information
    """
    try:
        if not artist and not mbid:
            return "Error: Either 'artist' name or 'mbid' must be provided"
        
        result = await artist_api.get_info(
            artist=artist,
            mbid=mbid,
            lang=lang,
            autocorrect=autocorrect,
            username=username
        )
        return result.to_string()
        
    except Exception as e:
        return f"Error getting artist info: {str(e)}"

@mcp.tool()
async def get_artist_top_albums(
    artist: str,
    mbid: Optional[str] = None,
    autocorrect: bool = True,
    limit: int = 10,
    page: int = 1
) -> str:
    """
    Get an artist's most popular albums
    
    Args:
        artist: Artist name
        mbid: Optional MBID (MusicBrainz ID) of the artist
        autocorrect: Whether to use autocorrection for the artist name
        limit: Maximum number of results to return (1-50, default: 10)
        page: Page number to retrieve (default: 1)
    
    Returns:
        Formatted list of the artist's top albums
    """
    try:
        limit = max(1, min(limit, 50))
        result = await artist_api.get_top_albums(
            artist=artist,
            mbid=mbid,
            autocorrect=autocorrect,
            limit=limit,
            page=page
        )
        return result.to_string()
        
    except Exception as e:
        return f"Error getting artist top albums: {str(e)}"

@mcp.tool()
async def get_artist_top_tracks(
    artist: str,
    mbid: Optional[str] = None,
    autocorrect: bool = True,
    limit: int = 10,
    page: int = 1
) -> str:
    """
    Get an artist's most popular tracks
    
    Args:
        artist: Artist name
        mbid: Optional MBID (MusicBrainz ID) of the artist
        autocorrect: Whether to use autocorrection for the artist name
        limit: Maximum number of results to return (1-50, default: 10)
        page: Page number to retrieve (default: 1)
    
    Returns:
        Formatted list of the artist's top tracks
    """
    try:
        limit = max(1, min(limit, 50))
        result = await artist_api.get_top_tracks(
            artist=artist,
            mbid=mbid,
            autocorrect=autocorrect,
            limit=limit,
            page=page
        )
        return result.to_string()
        
    except Exception as e:
        return f"Error getting artist top tracks: {str(e)}"

# ======= Album Tools =======

@mcp.tool()
async def search_albums(
    query: str,
    limit: int = 10,
    page: int = 1
) -> str:
    """
    Search for albums on Last.fm by name
    
    Args:
        query: Album name or search query
        limit: Maximum number of results to return (1-50, default: 10)
        page: Page number to retrieve (default: 1)
    
    Returns:
        Formatted list of matching albums with their stats
    """
    try:
        limit = max(1, min(limit, 50))
        result = await album_api.search(query, limit=limit, page=page)
        return result.to_string()
        
    except Exception as e:
        return f"Error searching albums: {str(e)}"

@mcp.tool()
async def get_album_info(
    artist: str,
    album: str,
    mbid: Optional[str] = None,
    autocorrect: bool = True,
    username: Optional[str] = None,
    lang: Optional[str] = None
) -> str:
    """
    Get detailed information about an album
    
    Args:
        artist: Artist name
        album: Album name
        mbid: Optional MBID (MusicBrainz ID) of the album
        autocorrect: Whether to use autocorrection for the names
        username: Username for personalized info (playcount, etc.)
        lang: Language code for wiki content
    
    Returns:
        Formatted detailed album information
    """
    try:
        result = await album_api.get_info(
            artist=artist,
            album=album,
            mbid=mbid,
            autocorrect=autocorrect,
            username=username,
            lang=lang
        )
        return result.to_string()
        
    except Exception as e:
        return f"Error getting album info: {str(e)}"

@mcp.tool()
async def get_album_top_tags(
    artist: str,
    album: str,
    mbid: Optional[str] = None,
    autocorrect: bool = True
) -> str:
    """
    Get tags associated with an album
    
    Args:
        artist: Artist name
        album: Album name
        mbid: Optional MBID (MusicBrainz ID) of the album
        autocorrect: Whether to use autocorrection for the names
    
    Returns:
        Formatted list of top tags for the album
    """
    try:
        result = await album_api.get_top_tags(
            artist=artist,
            album=album,
            mbid=mbid,
            autocorrect=autocorrect
        )
        return result.to_string()
        
    except Exception as e:
        return f"Error getting album top tags: {str(e)}"

# ======= Track Tools =======

@mcp.tool()
async def search_tracks(
    query: str,
    artist: Optional[str] = None,
    limit: int = 10,
    page: int = 1
) -> str:
    """
    Search for tracks on Last.fm by name
    
    Args:
        query: Track name or search query
        artist: Optional artist name to narrow search
        limit: Maximum number of results to return (1-50, default: 10)
        page: Page number to retrieve (default: 1)
    
    Returns:
        Formatted list of matching tracks with their stats
    """
    try:
        limit = max(1, min(limit, 50))
        result = await track_api.search(query, artist=artist, limit=limit, page=page)
        return result.to_string()
        
    except Exception as e:
        return f"Error searching tracks: {str(e)}"

@mcp.tool()
async def get_track_info(
    artist: str,
    track: str,
    mbid: Optional[str] = None,
    autocorrect: bool = True,
    username: Optional[str] = None
) -> str:
    """
    Get detailed information about a track
    
    Args:
        artist: Artist name
        track: Track name
        mbid: Optional MBID (MusicBrainz ID) of the track
        autocorrect: Whether to use autocorrection for the names
        username: Username for personalized info (playcount, etc.)
    
    Returns:
        Formatted detailed track information
    """
    try:
        result = await track_api.get_info(
            artist=artist,
            track=track,
            mbid=mbid,
            autocorrect=autocorrect,
            username=username
        )
        return result.to_string()
        
    except Exception as e:
        return f"Error getting track info: {str(e)}"

@mcp.tool()
async def get_similar_tracks(
    artist: str,
    track: str,
    mbid: Optional[str] = None,
    autocorrect: bool = True,
    limit: int = 10
) -> str:
    """
    Find tracks similar to a given track
    
    Args:
        artist: Artist name
        track: Track name
        mbid: Optional MBID (MusicBrainz ID) of the track
        autocorrect: Whether to use autocorrection for the names
        limit: Maximum number of similar tracks to return (1-30, default: 10)
    
    Returns:
        Formatted list of similar tracks
    """
    try:
        limit = max(1, min(limit, 30))
        result = await track_api.get_similar(
            artist=artist,
            track=track,
            mbid=mbid,
            autocorrect=autocorrect,
            limit=limit
        )
        return result.to_string()
        
    except Exception as e:
        return f"Error getting similar tracks: {str(e)}"

@mcp.tool()
async def get_track_top_tags(
    artist: str,
    track: str,
    mbid: Optional[str] = None,
    autocorrect: bool = True
) -> str:
    """
    Get tags associated with a track
    
    Args:
        artist: Artist name
        track: Track name
        mbid: Optional MBID (MusicBrainz ID) of the track
        autocorrect: Whether to use autocorrection for the names
    
    Returns:
        Formatted list of top tags for the track
    """
    try:
        result = await track_api.get_top_tags(
            artist=artist,
            track=track,
            mbid=mbid,
            autocorrect=autocorrect
        )
        return result.to_string()
        
    except Exception as e:
        return f"Error getting track top tags: {str(e)}"

# ======= User Tools =======

@mcp.tool()
async def get_user_info(
    user: str
) -> str:
    """
    Get user profile information
    
    Args:
        user: Username to get info for
    
    Returns:
        Formatted user profile information
    """
    try:
        result = await user_api.get_info(user=user)
        return result.to_string()
        
    except Exception as e:
        return f"Error getting user info: {str(e)}"

@mcp.tool()
async def get_user_recent_tracks(
    user: str,
    limit: int = 10,
    page: int = 1,
    from_timestamp: Optional[int] = None,
    to_timestamp: Optional[int] = None,
    extended: bool = False
) -> str:
    """
    Get a user's recently played tracks
    
    Args:
        user: Username
        limit: Maximum number of results to return (1-50, default: 10)
        page: Page number to retrieve (default: 1)
        from_timestamp: Unix timestamp to start from (optional)
        to_timestamp: Unix timestamp to end at (optional)
        extended: Include extended data (optional)
    
    Returns:
        Formatted list of user's recent tracks
    """
    try:
        limit = max(1, min(limit, 50))
        result = await user_api.get_recent_tracks(
            user=user,
            limit=limit,
            page=page,
            from_timestamp=from_timestamp,
            to_timestamp=to_timestamp,
            extended=extended
        )
        return result.to_string()
        
    except Exception as e:
        return f"Error getting user recent tracks: {str(e)}"

@mcp.tool()
async def get_user_top_artists(
    user: str,
    period: str = "overall",
    limit: int = 10,
    page: int = 1
) -> str:
    """
    Get a user's most played artists
    
    Args:
        user: Username
        period: Time period (7day, 1month, 3month, 6month, 12month, overall)
        limit: Maximum number of results to return (1-50, default: 10)
        page: Page number to retrieve (default: 1)
    
    Returns:
        Formatted list of user's top artists
    """
    try:
        limit = max(1, min(limit, 50))
        result = await user_api.get_top_artists(
            user=user,
            period=period,
            limit=limit,
            page=page
        )
        return result.to_string()
        
    except Exception as e:
        return f"Error getting user top artists: {str(e)}"

@mcp.tool()
async def get_user_top_albums(
    user: str,
    period: str = "overall",
    limit: int = 10,
    page: int = 1
) -> str:
    """
    Get a user's most played albums
    
    Args:
        user: Username
        period: Time period (7day, 1month, 3month, 6month, 12month, overall)
        limit: Maximum number of results to return (1-50, default: 10)
        page: Page number to retrieve (default: 1)
    
    Returns:
        Formatted list of user's top albums
    """
    try:
        limit = max(1, min(limit, 50))
        result = await user_api.get_top_albums(
            user=user,
            period=period,
            limit=limit,
            page=page
        )
        return result.to_string()
        
    except Exception as e:
        return f"Error getting user top albums: {str(e)}"

@mcp.tool()
async def get_user_top_tracks(
    user: str,
    period: str = "overall",
    limit: int = 10,
    page: int = 1
) -> str:
    """
    Get a user's most played tracks
    
    Args:
        user: Username
        period: Time period (7day, 1month, 3month, 6month, 12month, overall)
        limit: Maximum number of results to return (1-50, default: 10)
        page: Page number to retrieve (default: 1)
    
    Returns:
        Formatted list of user's top tracks
    """
    try:
        limit = max(1, min(limit, 50))
        result = await user_api.get_top_tracks(
            user=user,
            period=period,
            limit=limit,
            page=page
        )
        return result.to_string()
        
    except Exception as e:
        return f"Error getting user top tracks: {str(e)}"

@mcp.tool()
async def get_user_loved_tracks(
    user: str,
    limit: int = 10,
    page: int = 1
) -> str:
    """
    Get tracks a user has marked as loved
    
    Args:
        user: Username
        limit: Maximum number of results to return (1-50, default: 10)
        page: Page number to retrieve (default: 1)
    
    Returns:
        Formatted list of user's loved tracks
    """
    try:
        limit = max(1, min(limit, 50))
        result = await user_api.get_loved_tracks(
            user=user,
            limit=limit,
            page=page
        )
        return result.to_string()
        
    except Exception as e:
        return f"Error getting user loved tracks: {str(e)}"

# ======= Tag Tools =======

@mcp.tool()
async def get_tag_info(
    tag: str,
    lang: Optional[str] = None
) -> str:
    """
    Get information about a music tag
    
    Args:
        tag: Tag name
        lang: Language code for wiki content (optional)
    
    Returns:
        Formatted tag information
    """
    try:
        result = await tag_api.get_info(tag=tag, lang=lang)
        return result.to_string()
        
    except Exception as e:
        return f"Error getting tag info: {str(e)}"

@mcp.tool()
async def get_tag_top_artists(
    tag: str,
    limit: int = 10,
    page: int = 1
) -> str:
    """
    Get top artists for a tag
    
    Args:
        tag: Tag name
        limit: Maximum number of results to return (1-50, default: 10)
        page: Page number to retrieve (default: 1)
    
    Returns:
        Formatted list of top artists for the tag
    """
    try:
        limit = max(1, min(limit, 50))
        result = await tag_api.get_top_artists(tag=tag, limit=limit, page=page)
        return result.to_string()
        
    except Exception as e:
        return f"Error getting tag top artists: {str(e)}"

@mcp.tool()
async def get_tag_top_albums(
    tag: str,
    limit: int = 10,
    page: int = 1
) -> str:
    """
    Get top albums for a tag
    
    Args:
        tag: Tag name
        limit: Maximum number of results to return (1-50, default: 10)
        page: Page number to retrieve (default: 1)
    
    Returns:
        Formatted list of top albums for the tag
    """
    try:
        limit = max(1, min(limit, 50))
        result = await tag_api.get_top_albums(tag=tag, limit=limit, page=page)
        return result.to_string()
        
    except Exception as e:
        return f"Error getting tag top albums: {str(e)}"

@mcp.tool()
async def get_tag_top_tracks(
    tag: str,
    limit: int = 10,
    page: int = 1
) -> str:
    """
    Get top tracks for a tag
    
    Args:
        tag: Tag name
        limit: Maximum number of results to return (1-50, default: 10)
        page: Page number to retrieve (default: 1)
    
    Returns:
        Formatted list of top tracks for the tag
    """
    try:
        limit = max(1, min(limit, 50))
        result = await tag_api.get_top_tracks(tag=tag, limit=limit, page=page)
        return result.to_string()
        
    except Exception as e:
        return f"Error getting tag top tracks: {str(e)}"

@mcp.tool()
async def get_tag_weekly_charts(
    tag: str
) -> str:
    """
    Get weekly chart data for a tag
    
    Args:
        tag: Tag name
    
    Returns:
        Formatted list of available weekly chart periods
    """
    try:
        result = await tag_api.get_weekly_chart_list(tag=tag)
        return result.to_string()
        
    except Exception as e:
        return f"Error getting tag weekly charts: {str(e)}"

# ======= Chart Tools =======

@mcp.tool()
async def get_top_artists(
    limit: int = 10,
    page: int = 1
) -> str:
    """
    Get global top artists chart
    
    Args:
        limit: Maximum number of results to return (1-50, default: 10)
        page: Page number to retrieve (default: 1)
    
    Returns:
        Formatted list of global top artists
    """
    try:
        limit = max(1, min(limit, 50))
        result = await chart_api.get_top_artists(limit=limit, page=page)
        return result.to_string()
        
    except Exception as e:
        return f"Error getting top artists: {str(e)}"

@mcp.tool()
async def get_top_tracks(
    limit: int = 10,
    page: int = 1
) -> str:
    """
    Get global top tracks chart
    
    Args:
        limit: Maximum number of results to return (1-50, default: 10)
        page: Page number to retrieve (default: 1)
    
    Returns:
        Formatted list of global top tracks
    """
    try:
        limit = max(1, min(limit, 50))
        result = await chart_api.get_top_tracks(limit=limit, page=page)
        return result.to_string()
        
    except Exception as e:
        return f"Error getting top tracks: {str(e)}"

@mcp.tool()
async def get_top_tags(
    limit: int = 10,
    page: int = 1
) -> str:
    """
    Get global top tags chart
    
    Args:
        limit: Maximum number of results to return (1-50, default: 10)
        page: Page number to retrieve (default: 1)
    
    Returns:
        Formatted list of global top tags
    """
    try:
        limit = max(1, min(limit, 50))
        result = await chart_api.get_top_tags(limit=limit, page=page)
        return result.to_string()
        
    except Exception as e:
        return f"Error getting top tags: {str(e)}"

# ======= Authentication Tools =======

@mcp.tool()
async def check_auth_status() -> str:
    """
    Check if the user is authenticated.
    Authentication is required to use the following tools:
    - scrobble_track
    - update_now_playing
    - love_track
    - unlove_track
    - add_tags
    - remove_tag

    Args:
        None

    Returns:
        "Authenticated" if the user is authenticated, "Not authenticated" otherwise
    """
    try:
        session_key = os.getenv("LASTFM_SESSION_KEY")
        if not session_key:
            return "Not authenticated. No session key found in environment."
        
        result = await auth_api.validate_session(session_key)   
        if result:
            return "Authenticated"
        else:
            return "Not authenticated"
    except Exception as e:
        return f"Error checking auth status: {str(e)}"

@mcp.tool()
async def authenticate_user() -> str:
    """
    Starts the authentication process - sets the token in the environment variable and returns an auth URL for the user to visit.
    """
    try:
        result = await auth_api.get_token()
        
        os.environ["LASTFM_TOKEN"] = result["token"]
        
        return f"Visit {result['auth_url']} to authorize, then use get_session() to complete authentication."
        
    except Exception as e:
        return f"Error starting authentication: {str(e)}"

@mcp.tool()
async def get_session() -> str:
    """
    Complete the authentication process by getting a session key from the authorized token.
    This should be called after the user has visited the authorization URL from authenticate_user().
    """
    try:
        token = os.getenv("LASTFM_TOKEN")
        if not token:
            return "No token found. Please run authenticate_user() first to get a token."
        
        result = await auth_api.get_session(token)
        
        os.environ["LASTFM_SESSION_KEY"] = result["session_key"]
        
        return f"Authentication successful for user {result['username']}. Session key stored in environment."
    except Exception as e:
        return f"Error completing authentication: {str(e)}"

# ======= Authentication Tools =======

@mcp.tool()
async def scrobble_track(
    artist: str,
    track: str,
    timestamp: Optional[int] = None,
    album: Optional[str] = None,
    duration: Optional[int] = None,
    mbid: Optional[str] = None
) -> str:
    """
    Scrobble a track to your Last.fm profile.
    Requires authentication - use authenticate_user() and get_session() first.
    
    Args:
        artist: Artist name
        track: Track name
        timestamp: Unix timestamp when track was played (optional, defaults to current time)
        album: Album name (optional)
        duration: Track duration in seconds (optional)
        mbid: MusicBrainz Track ID (optional, more accurate than name)
    
    Returns:
        Confirmation of scrobble action
    """
    try:
        # Check if user is authenticated
        session_key = os.getenv("LASTFM_SESSION_KEY")
        if not session_key:
            return "Not authenticated. Please use authenticate_user() and get_session() first."
        
        # Use provided timestamp or current time
        if timestamp is None:
            timestamp = int(time.time())
        
        result = await track_api.scrobble(
            artist=artist,
            track=track,
            timestamp=timestamp,
            session_key=session_key,
            album=album,
            duration=duration,
            mbid=mbid
        )
        
        if result["accepted"] == 1:
            return f"Successfully scrobbled '{track}' by {artist}"
        else:
            return f"Scrobble failed. Accepted: {result['accepted']}, Ignored: {result['ignored']}"
            
    except Exception as e:
        return f"Error scrobbling track: {str(e)}"

@mcp.tool()
async def update_now_playing(
    artist: str,
    track: str,
    album: Optional[str] = None,
    duration: Optional[int] = None,
    mbid: Optional[str] = None
) -> str:
    """
    Update your "now playing" status on Last.fm.
    Requires authentication - use authenticate_user() and get_session() first.
    
    Args:
        artist: Artist name
        track: Track name
        album: Album name (optional)
        duration: Track duration in seconds (optional)
        mbid: MusicBrainz Track ID (optional)
    
    Returns:
        Confirmation of now playing update
    """
    try:
        session_key = os.getenv("LASTFM_SESSION_KEY")
        if not session_key:
            return "Not authenticated. Please use authenticate_user() and get_session() first."
        
        result = await track_api.update_now_playing(
            artist=artist,
            track=track,
            session_key=session_key,
            album=album,
            duration=duration,
            mbid=mbid
        )
        
        return f"Now playing: '{result['track']}' by {result['artist']}"
        
    except Exception as e:
        return f"Error updating now playing: {str(e)}"

@mcp.tool()
async def love_track(
    artist: str,
    track: str
) -> str:
    """
    Love a track on your Last.fm profile.
    Requires authentication - use authenticate_user() and get_session() first.
    
    Args:
        artist: Artist name
        track: Track name
    
    Returns:
        Confirmation of love action
    """
    try:
        session_key = os.getenv("LASTFM_SESSION_KEY")
        if not session_key:
            return "Not authenticated. Please use authenticate_user() and get_session() first."
        
        result = await track_api.love(
            artist=artist,
            track=track,
            session_key=session_key
        )
        
        return f"Loved '{track}' by {artist}"
        
    except Exception as e:
        return f"Error loving track: {str(e)}"

@mcp.tool()
async def unlove_track(
    artist: str,
    track: str
) -> str:
    """
    Remove love from a track on your Last.fm profile.
    Requires authentication - use authenticate_user() and get_session() first.
    
    Args:
        artist: Artist name
        track: Track name
    
    Returns:
        Confirmation of unlove action
    """
    try:
        session_key = os.getenv("LASTFM_SESSION_KEY")
        if not session_key:
            return "Not authenticated. Please use authenticate_user() and get_session() first."
        
        result = await track_api.unlove(
            artist=artist,
            track=track,
            session_key=session_key
        )
        
        return f"Removed love from '{track}' by {artist}"
        
    except Exception as e:
        return f"Error unloving track: {str(e)}"

@mcp.tool()
async def add_tags(
    artist: str,
    track: str,
    tags: str
) -> str:
    """
    Add tags to a track on your Last.fm profile.
    Requires authentication - use authenticate_user() and get_session() first.
    
    Args:
        artist: Artist name
        track: Track name
        tags: Comma-separated list of tags (max 10)
    
    Returns:
        Confirmation of tag addition
    """
    try:
        session_key = os.getenv("LASTFM_SESSION_KEY")
        if not session_key:
            return "Not authenticated. Please use authenticate_user() and get_session() first."
        
        result = await track_api.add_tags(
            artist=artist,
            track=track,
            tags=tags,
            session_key=session_key
        )
        
        return f"Added tags to '{track}' by {artist}: {', '.join(result['tags'])}"
        
    except Exception as e:
        return f"Error adding tags: {str(e)}"

@mcp.tool()
async def remove_tag(
    artist: str,
    track: str,
    tag: str
) -> str:
    """
    Remove a tag from a track on your Last.fm profile.
    Requires authentication - use authenticate_user() and get_session() first.
    
    Args:
        artist: Artist name
        track: Track name
        tag: Tag to remove
    
    Returns:
        Confirmation of tag removal
    """
    try:
        session_key = os.getenv("LASTFM_SESSION_KEY")
        if not session_key:
            return "Not authenticated. Please use authenticate_user() and get_session() first."
        
        result = await track_api.remove_tag(
            artist=artist,
            track=track,
            tag=tag,
            session_key=session_key
        )
        
        return f"Removed tag '{tag}' from '{track}' by {artist}"
        
    except Exception as e:
        return f"Error removing tag: {str(e)}"

if __name__ == "__main__":
    try:
        mcp.run()
    except KeyboardInterrupt:
        pass
    except Exception as e:
        logger.error(f"Server error: {e}")
        sys.exit(1)
