"""
Tag-related Pydantic models
"""

from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field, validator
from src.models.base import LastFmImage


class Tag(BaseModel):
    """Tag information"""
    name: str
    url: str = ""
    reach: Optional[int] = None
    taggings: Optional[int] = None
    
    @validator('reach', 'taggings', pre=True)
    def convert_to_int(cls, v):
        """Convert string numbers to integers"""
        if v is None:
            return None
        if isinstance(v, str):
            return int(v) if v.isdigit() else 0
        return v or 0
    
    @classmethod
    def from_lastfm_tag(cls, tag_data: Dict[str, Any]) -> "Tag":
        """Convert Last.fm tag data to model"""
        return cls(
            name=tag_data.get("name", ""),
            url=tag_data.get("url", ""),
            reach=tag_data.get("reach"),
            taggings=tag_data.get("taggings")
        )


class TaggedArtist(BaseModel):
    """Artist with tag weight"""
    name: str
    mbid: str = ""
    url: str = ""
    streamable: bool = False
    image: Optional[LastFmImage] = None
    
    @classmethod
    def from_lastfm_tagged(cls, tagged_data: Dict[str, Any]) -> "TaggedArtist":
        """Convert Last.fm tagged artist to model"""
        return cls(
            name=tagged_data.get("name", ""),
            mbid=tagged_data.get("mbid", ""),
            url=tagged_data.get("url", ""),
            streamable=tagged_data.get("streamable", "0") == "1",
            image=LastFmImage.from_lastfm_images(tagged_data.get("image", []))
        )


class TagTopArtistsResponse(BaseModel):
    """Response for tag.getTopArtists"""
    tag: str = ""
    total: int = 0
    page: int = 1
    per_page: int = 50
    artists: List[TaggedArtist] = Field(default_factory=list)
