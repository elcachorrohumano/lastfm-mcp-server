# Last.fm MCP Server

A Model Context Protocol (MCP) server that provides access to Last.fm music data and discovery capabilities.

## Available Tools

### Artist Tools
- `search_artists` - Search for artists by name
- `get_artist_info` - Get detailed artist information and biography
- `get_artist_top_albums` - Get an artist's most popular albums
- `get_artist_top_tracks` - Get an artist's most popular tracks

### Album Tools
- `search_albums` - Search for albums by name
- `get_album_info` - Get detailed album information and tracklist
- `get_album_top_tags` - Get tags associated with an album

### Track Tools
- `search_tracks` - Search for tracks by name
- `get_track_info` - Get detailed track information
- `get_similar_tracks` - Find tracks similar to a given track
- `get_track_top_tags` - Get tags associated with a track

### User Tools
- `get_user_info` - Get user profile information
- `get_user_recent_tracks` - Get a user's recently played tracks
- `get_user_top_artists` - Get a user's most played artists
- `get_user_top_albums` - Get a user's most played albums
- `get_user_top_tracks` - Get a user's most played tracks
- `get_user_loved_tracks` - Get tracks a user has marked as loved

### Chart Tools
- `get_top_artists` - Get global top artists
- `get_top_tracks` - Get global top tracks
- `get_top_tags` - Get popular music tags

### Tag Tools
- `get_tag_info` - Get information about a music tag
- `get_tag_top_artists` - Get top artists for a tag
- `get_tag_top_albums` - Get top albums for a tag
- `get_tag_top_tracks` - Get top tracks for a tag
- `get_tag_weekly_charts` - Get weekly chart data for a tag

### Write Operations (Authentication Required)
- `scrobble_track` - Scrobble a track to user's profile
- `love_track` - Mark a track as loved
- `unlove_track` - Remove love from a track
- `update_now_playing` - Update what's currently playing
- `add_track_tags` - Add tags to a track
- `remove_track_tag` - Remove a tag from a track

### Authentication Tools
- `get_auth_token` - Get authentication token for user login
- `get_auth_session` - Convert token to session for API access

## Setup

### Prerequisites
1. Get Last.fm API credentials at [Last.fm API](https://www.last.fm/api/account/create)
2. Copy `.env.example` to `.env` and add your credentials:
   ```env
   LASTFM_API_KEY=your_actual_api_key_here
   LASTFM_SHARED_SECRET=your_actual_shared_secret_here
   ```

### VS Code/Cursor Setup

#### Option 1: Docker (Recommended)
First build the image:
```bash
docker build -t lastfm-mcp .
```

Then add to your VS Code/Cursor MCP configuration:
```json
{
  "mcpServers": {
    "lastfm-mcp": {
      "command": "docker",
      "args": [
        "run",
        "--rm",
        "-i",
        "--env-file",
        "/path/to/your/.env",
        "lastfm-mcp"
      ]
    }
  }
}
```

**Important**: Replace `/path/to/your/.env` with the actual path to your `.env` file.

#### Option 2: UV
Add to your VS Code/Cursor MCP configuration:

```json
{
  "mcpServers": {
    "lastfm-mcp": {
      "command": "/path/to/uv",
      "args": [
        "--directory",
        "/path/to/your/project",
        "run",
        "--env-file",
        ".env",
        "mcp_server.py"
      ]
    }
  }
}
```

**Important**: 
- Replace `/path/to/uv` with the actual path to your UV installation. Run `which uv` in your terminal to find the path (e.g., `/usr/local/bin/uv`, `/home/user/.local/bin/uv`, or just `uv` if it's in your PATH)
- Replace `/path/to/your/project` with the actual absolute path to your project directory
