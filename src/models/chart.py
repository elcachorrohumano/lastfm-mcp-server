"""
Chart-related Pydantic models
"""

from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field, validator
from src.models.base import LastFmImage


class ChartArtist(BaseModel):
    """Artist from charts"""
    name: str
    mbid: str = ""
    url: str = ""
    playcount: int = 0
    listeners: int = 0
    image: Optional[LastFmImage] = None
    
    @validator('playcount', 'listeners', pre=True)
    def convert_to_int(cls, v):
        """Convert string numbers to integers"""
        if isinstance(v, str):
            return int(v) if v.isdigit() else 0
        return v or 0
    
    @classmethod
    def from_lastfm_chart(cls, chart_data: Dict[str, Any]) -> "ChartArtist":
        """Convert Last.fm chart artist to model"""
        return cls(
            name=chart_data.get("name", ""),
            mbid=chart_data.get("mbid", ""),
            url=chart_data.get("url", ""),
            playcount=chart_data.get("playcount", 0),
            listeners=chart_data.get("listeners", 0),
            image=LastFmImage.from_lastfm_images(chart_data.get("image", []))
        )


class ChartResponse(BaseModel):
    """Chart response with pagination"""
    page: int = 1
    per_page: int = 50
    total: int = 0
    total_pages: int = 1
    artists: List[ChartArtist] = Field(default_factory=list)
