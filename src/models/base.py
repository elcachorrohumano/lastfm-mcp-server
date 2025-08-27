"""
Base models shared across all Last.fm endpoints
"""

from typing import List, Dict, Any, Union, Optional
from pydantic import BaseModel, validator


class LastFmImage(BaseModel):
    """Last.fm image with different sizes"""
    small: str = ""
    medium: str = ""
    large: str = ""
    extralarge: str = ""
    mega: str = ""
    
    @classmethod
    def from_lastfm_images(cls, images: List[Dict[str, Any]]) -> "LastFmImage":
        """Convert Last.fm image array to structured model"""
        image_dict = {}
        for img in images:
            if isinstance(img, dict) and "size" in img:
                size = img["size"]
                url = img.get("#text", "")
                if size:  # Skip empty size keys
                    image_dict[size] = url
        return cls(**image_dict)


class LastFmStats(BaseModel):
    """Statistics for artists, albums, tracks"""
    listeners: int = 0
    playcount: int = 0
    user_playcount: Optional[int] = None  # User-specific playcount when username is provided
    
    @validator('listeners', 'playcount', 'user_playcount', pre=True)
    def convert_to_int(cls, v):
        """Convert string numbers to integers"""
        if isinstance(v, str):
            return int(v) if v.isdigit() else 0
        return v or 0


class LastFmDate(BaseModel):
    """Last.fm date with timestamp"""
    timestamp: Optional[int] = None
    text: Optional[str] = None
    
    @classmethod
    def from_lastfm_date(cls, date_data: Union[Dict, str, int, None]) -> "LastFmDate":
        """Convert various Last.fm date formats"""
        if isinstance(date_data, dict):
            return cls(
                timestamp=date_data.get("uts"),
                text=date_data.get("#text")
            )
        elif isinstance(date_data, str):
            return cls(text=date_data)
        elif isinstance(date_data, int):
            return cls(timestamp=date_data)
        return cls()
