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

@mcp.tool()
async def search_artists(query: str, limit: int = 10) -> str:
    """
    Search for artists on Last.fm by name
    
    Args:
        query: Artist name or search query
        limit: Maximum number of results to return (1-50, default: 10)
    
    Returns:
        Formatted list of matching artists with their stats
    """
    try:
        limit = max(1, min(limit, 50))
        result = await artist_api.search(query, limit=limit)
        return result.to_string()
        
    except Exception as e:
        return f"Error searching artists: {str(e)}"









if __name__ == "__main__":
    try:
        mcp.run()
    except KeyboardInterrupt:
        pass
    except Exception as e:
        logger.error(f"Server error: {e}")
        sys.exit(1)
