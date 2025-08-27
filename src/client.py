import hashlib
import httpx
from typing import Dict, Any, Optional
import os
from dotenv import load_dotenv



load_dotenv()


class LastFmApiError(Exception):
    """Custom exception for Last.fm API errors"""
    def __init__(self, error_code: int, message: str):
        self.error_code = error_code
        self.message = message
        super().__init__(f"Last.fm API Error {error_code}: {message}")


class LastFmClient:
    """
    Core Last.fm API client for making HTTP requests
    Handles both simple (read-only) and authenticated (write) operations
    """
    
    def __init__(self, api_key: str = None, shared_secret: str = None):
        self.api_key = api_key or os.getenv("LASTFM_API_KEY")
        self.shared_secret = shared_secret or os.getenv("LASTFM_SHARED_SECRET")
        self.base_url = "https://ws.audioscrobbler.com/2.0/"
        
        if not self.api_key:
            raise ValueError("Last.fm API key is required")
    
    def _generate_signature(self, params: Dict[str, Any]) -> str:
        """
        Generate MD5 signature for authenticated API calls
        Required for write operations and user authentication
        """
        if not self.shared_secret:
            raise ValueError("Shared secret required for signed requests")
        
        # Sort parameters and create signature string
        sorted_params = sorted(params.items())
        signature_string = "".join(f"{key}{value}" for key, value in sorted_params)
        signature_string += self.shared_secret
        
        return hashlib.md5(signature_string.encode('utf-8')).hexdigest()
    
    def _prepare_params(self, method: str, params: Dict[str, Any], signed: bool = False) -> Dict[str, Any]:
        """
        Prepare parameters for API request
        Adds common parameters and signature if required
        """
        # Start with method-specific parameters
        request_params = params.copy()
        
        # Add common parameters
        request_params.update({
            "method": method,
            "api_key": self.api_key,
            "format": "json"
        })
        
        # Add signature for authenticated requests
        if signed:
            # Remove format from signature calculation (not included in signature)
            sig_params = {k: v for k, v in request_params.items() if k != "format"}
            request_params["api_sig"] = self._generate_signature(sig_params)
        
        return request_params
    
    def _handle_response(self, response_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Handle Last.fm API response and check for errors
        """
        # Check for API errors
        if "error" in response_data:
            error_code = response_data.get("error", 0)
            error_message = response_data.get("message", "Unknown error")
            raise LastFmApiError(error_code, error_message)
        
        return response_data
    
    async def _make_request(
        self, 
        method: str, 
        params: Dict[str, Any] = None, 
        signed: bool = False,
        http_method: str = "GET"
    ) -> Dict[str, Any]:
        """
        Make HTTP request to Last.fm API
        
        Args:
            method: Last.fm API method (e.g., 'artist.getinfo')
            params: Method-specific parameters
            signed: Whether request requires authentication signature
            http_method: HTTP method ('GET' or 'POST')
        """
        if params is None:
            params = {}
        
        # Prepare request parameters
        request_params = self._prepare_params(method, params, signed)
        
        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                if http_method.upper() == "POST":
                    response = await client.post(self.base_url, data=request_params)
                else:
                    response = await client.get(self.base_url, params=request_params)
                
                response.raise_for_status()
                response_data = response.json()
                
                return self._handle_response(response_data)
                
        except httpx.HTTPStatusError as e:
            raise LastFmApiError(e.response.status_code, f"HTTP error: {e}")
        except httpx.RequestError as e:
            raise LastFmApiError(0, f"Request error: {e}")
        except Exception as e:
            raise LastFmApiError(0, f"Unexpected error: {e}")
