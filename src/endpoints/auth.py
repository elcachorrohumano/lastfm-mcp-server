from typing import Dict, Any, Optional
from src.client import LastFmClient


class AuthEndpoints:
    """
    Authentication-related Last.fm API endpoints
    Provides clean interface for user authentication flow
    """
    
    def __init__(self, client: LastFmClient):
        self.client = client
    
    async def get_token(self) -> Dict[str, Any]:
        """
        Get a request token for authentication
        This is the first step in the authentication process
        
        Returns:
            Dictionary containing the token and authentication URL
        """
        raw_result = await self.client._make_request("auth.getToken", {}, signed=True)
        token = raw_result.get("token", "")
        
        return {
            "token": token,
            "auth_url": f"http://www.last.fm/api/auth/?api_key={self.client.api_key}&token={token}",
            "instructions": "Visit the auth_url to authorize the application, then use get_session() with this token"
        }
    
    async def get_session(self, token: str) -> Dict[str, Any]:
        """
        Get a session key from an authorized token
        Call this after the user has authorized the token via the web interface
        
        Args:
            token: The authorized token from get_token()
        
        Returns:
            Dictionary containing session key and user info
        """
        params = {
            "token": token
        }
        
        raw_result = await self.client._make_request("auth.getSession", params, signed=True)
        session_data = raw_result.get("session", {})
        
        return {
            "session_key": session_data.get("key", ""),
            "username": session_data.get("name", ""),
            "subscriber": session_data.get("subscriber", "0") == "1"
        }
    
    async def get_mobile_session(self, username: str, password: str) -> Dict[str, Any]:
        """
        Get a mobile session (direct username/password authentication)
        Note: This method is deprecated by Last.fm and may not work for all users
        
        Args:
            username: Last.fm username
            password: Last.fm password
        
        Returns:
            Dictionary containing session key and user info
        """
        params = {
            "username": username,
            "password": password
        }
        
        raw_result = await self.client._make_request("auth.getMobileSession", params, signed=True, http_method="POST")
        session_data = raw_result.get("session", {})
        
        return {
            "session_key": session_data.get("key", ""),
            "username": session_data.get("name", ""),
            "subscriber": session_data.get("subscriber", "0") == "1"
        }
