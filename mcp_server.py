#!/usr/bin/env python3
"""
Last.fm MCP Server
Provides Last.fm music data and discovery tools for AI assistants
"""

import asyncio
import logging
import os
import sys
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
        autocorrect: Whether to use autocorrection for the artist name (if the name was provided)
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
        
        # Format the response
        return result.to_string()
        
    except Exception as e:
        return f"Error getting artist info: {str(e)}"


if __name__ == "__main__":
    try:
        mcp.run()
    except KeyboardInterrupt:
        pass
    except Exception as e:
        logger.error(f"Server error: {e}")
        sys.exit(1)
