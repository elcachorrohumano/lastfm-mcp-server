from typing import Dict, Any, Optional
from src.client import LastFmClient, LastFmApiError


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
        raw_result = await self.client._make_request("auth.getToken", {})
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
        
        try:
            # Check if we have shared secret for signature
            if not self.client.shared_secret:
                print("Warning: No LASTFM_SHARED_SECRET found. This may cause authentication to fail.")
                print("Please set LASTFM_SHARED_SECRET in your .env file")
            
            # Try without signature first (some auth endpoints don't require it)
            try:
                raw_result = await self.client._make_request("auth.getSession", params, signed=False)
            except Exception as e:
                if "400" in str(e) and self.client.shared_secret:
                    print("Trying with signature...")
                    raw_result = await self.client._make_request("auth.getSession", params, signed=True)
                else:
                    raise e
            
            session_data = raw_result.get("session", {})
            
            return {
                "session_key": session_data.get("key", ""),
                "username": session_data.get("name", ""),
                "subscriber": session_data.get("subscriber", "0") == "1"
            }
        except Exception as e:
            print(f"Debug: Full error details: {e}")
            # Let's also try to get more details about the request
            print(f"Debug: Token being used: {token}")
            print(f"Debug: API Key: {self.client.api_key}")
            print(f"Debug: Shared Secret available: {'Yes' if self.client.shared_secret else 'No'}")
            raise e
    
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
        
        raw_result = await self.client._make_request("auth.getMobileSession", params, http_method="POST")
        session_data = raw_result.get("session", {})
        
        return {
            "session_key": session_data.get("key", ""),
            "username": session_data.get("name", ""),
            "subscriber": session_data.get("subscriber", "0") == "1"
        }
    
    async def validate_session(self, session_key: str) -> bool:
        """
        Validate if a session key is still valid
        Uses user.getInfo as a lightweight authentication test
        
        Args:
            session_key: The session key to validate
        
        Returns:
            True if session is valid, False otherwise
        """
        try:
            # Use a lightweight endpoint that requires auth
            result = await self.client._make_request("user.getInfo", {"sk": session_key})
            return True
        except LastFmApiError as e:
            if e.error_code == 9:  # Invalid session key
                return False
            raise e
