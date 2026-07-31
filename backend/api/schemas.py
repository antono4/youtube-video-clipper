"""
Pydantic schemas for API request/response validation.
"""
from pydantic import BaseModel, Field, field_validator
from typing import Optional
import re


class URLValidationRequest(BaseModel):
    """Request model for URL validation."""
    url: str = Field(..., description="YouTube video URL")
    
    @field_validator('url')
    @classmethod
    def validate_youtube_url(cls, v: str) -> str:
        """Validate YouTube URL format."""
        youtube_patterns = [
            r'(https?://)?(www\.)?youtube\.com/watch\?v=[\w-]+',
            r'(https?://)?youtu\.be/[\w-]+',
            r'(https?://)?(www\.)?youtube\.com/embed/[\w-]+',
            r'(https?://)?(www\.)?youtube\.com/shorts/[\w-]+',
        ]
        if not any(re.match(pattern, v) for pattern in youtube_patterns):
            raise ValueError('Invalid YouTube URL format')
        return v


class VideoInfoResponse(BaseModel):
    """Response model for video information."""
    video_id: str
    title: str
    duration: int  # seconds
    thumbnail: str
    uploader: str
    description: str


class ClipRequest(BaseModel):
    """Request model for clip processing."""
    url: str = Field(..., description="YouTube video URL")
    start_time: int = Field(..., ge=0, description="Start time in seconds")
    end_time: int = Field(..., gt=0, description="End time in seconds")
    
    @field_validator('end_time')
    @classmethod
    def validate_end_time(cls, v: int, info) -> int:
        """Validate end_time is after start_time."""
        if 'start_time' in info.data and v <= info.data['start_time']:
            raise ValueError('end_time must be greater than start_time')
        return v


class ClipResponse(BaseModel):
    """Response model for clip processing."""
    success: bool
    message: str
    file_path: Optional[str] = None
    file_size: Optional[int] = None
    session_id: Optional[str] = None


class ProcessingStatusResponse(BaseModel):
    """Response model for processing status."""
    status: str  # pending, processing, completed, failed
    progress: float  # 0.0 to 1.0
    message: Optional[str] = None


class URLShortenRequest(BaseModel):
    """Request model for URL shortening."""
    url: str = Field(..., min_length=1, description="URL to shorten")


class URLShortenResponse(BaseModel):
    """Response model for URL shortening."""
    success: bool
    original_url: Optional[str] = None
    short_url: Optional[str] = None
    short_url_2: Optional[str] = None
    short_url_3: Optional[str] = None
    share_url: Optional[str] = None
    error: Optional[str] = None


class ThumbnailRequest(BaseModel):
    """Request model for thumbnail generation."""
    video_id: str = Field(..., description="YouTube video ID")
    quality: str = Field(default="maxresdefault", description="Thumbnail quality")


class ThumbnailResponse(BaseModel):
    """Response model for thumbnail generation."""
    success: bool
    video_id: Optional[str] = None
    thumbnail_url: Optional[str] = None
    thumbnails: Optional[dict] = None
    error: Optional[str] = None


class CloudUploadRequest(BaseModel):
    """Request model for cloud upload."""
    session_id: str = Field(..., min_length=1, description="Session ID of the clip to upload")


class CloudUploadResponse(BaseModel):
    """Response model for cloud upload."""
    success: bool
    download_page: Optional[str] = None
    direct_link: Optional[str] = None
    file_name: Optional[str] = None
    error: Optional[str] = None


class VideoMetadataResponse(BaseModel):
    """Response model for video metadata."""
    success: bool
    author_name: Optional[str] = None
    author_url: Optional[str] = None
    thumbnail_url: Optional[str] = None
    html_embed: Optional[str] = None
    width: Optional[int] = None
    height: Optional[int] = None
    error: Optional[str] = None


class ClipStatsResponse(BaseModel):
    """Response model for clip statistics."""
    success: bool
    session_id: str
    clip_duration: int
    clip_size: int
    created_at: Optional[str] = None
    file_path: str