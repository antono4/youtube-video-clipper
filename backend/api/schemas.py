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