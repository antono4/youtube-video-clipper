"""
FastAPI routes for the YouTube Video Clipper API.
"""
from fastapi import APIRouter, HTTPException
from fastapi.responses import FileResponse
from datetime import datetime
import os

from backend.api.schemas import (
    URLValidationRequest,
    VideoInfoResponse,
    ClipRequest,
    ClipResponse,
    URLShortenRequest,
    URLShortenResponse,
    ThumbnailRequest,
    ThumbnailResponse,
    CloudUploadRequest,
    CloudUploadResponse,
    VideoMetadataResponse,
    ClipStatsResponse,
)
from backend.services.video_service import video_service
from backend.services.external_services import (
    url_shortener_service,
    screenshot_service,
    cloud_upload_service,
    video_metadata_service,
)
from backend.core.config import settings
from backend.core.exceptions import VideoProcessingError, FFmpegError

router = APIRouter()


@router.post("/api/validate", response_model=VideoInfoResponse)
async def validate_url(request: URLValidationRequest):
    """
    Validate YouTube URL and return video information.
    """
    try:
        info = video_service.get_video_info(request.url)
        return info
    except VideoProcessingError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal error: {str(e)}")


@router.post("/api/process", response_model=ClipResponse)
async def process_clip(request: ClipRequest):
    """
    Process video clip from YouTube URL.
    """
    try:
        # Validate clip duration
        clip_duration = request.end_time - request.start_time
        
        if clip_duration <= 0:
            return ClipResponse(
                success=False,
                message="Waktu selesai harus lebih besar dari waktu mulai"
            )
        
        if clip_duration > settings.MAX_CLIP_DURATION:
            return ClipResponse(
                success=False,
                message=f"Durasi klip maksimal adalah {settings.MAX_CLIP_DURATION // 60} menit"
            )
        
        # Create session
        session_id = video_service.create_session()
        
        # Process clip
        file_path, file_size = video_service.process_clip(
            url=request.url,
            start_time=request.start_time,
            end_time=request.end_time,
            session_id=session_id
        )
        
        return ClipResponse(
            success=True,
            message="Clip berhasil dibuat!",
            file_path=f"/api/download/{session_id}",
            file_size=file_size,
            session_id=session_id
        )
        
    except VideoProcessingError as e:
        return ClipResponse(success=False, message=str(e))
    except FFmpegError as e:
        return ClipResponse(success=False, message=str(e))
    except Exception as e:
        return ClipResponse(success=False, message=f"Error: {str(e)}")


@router.get("/api/download/{session_id}")
async def download_clip(session_id: str):
    """
    Download the processed clip file.
    """
    file_path = settings.TEMP_DIR / session_id / "output.mp4"
    
    if not file_path.exists():
        raise HTTPException(status_code=404, detail="File tidak ditemukan atau sudah kadaluwarsa")
    
    return FileResponse(
        path=str(file_path),
        media_type="video/mp4",
        filename="clip.mp4"
    )


@router.delete("/api/cleanup/{session_id}")
async def cleanup_session(session_id: str):
    """
    Clean up session files.
    """
    video_service.cleanup_session(session_id)
    return {"message": "Session cleaned up"}


# ========== New Feature Endpoints ==========

@router.post("/api/shorten", response_model=URLShortenResponse)
async def shorten_url(request: URLShortenRequest):
    """
    Shorten a URL using Shrtco.de API.
    """
    result = await url_shortener_service.shorten_url(request.url)
    return URLShortenResponse(**result)


@router.get("/api/thumbnail/{video_id}", response_model=ThumbnailResponse)
async def get_thumbnail(video_id: str, quality: str = "maxresdefault"):
    """
    Get YouTube video thumbnail URLs.
    """
    thumbnail_url = screenshot_service.generate_youtube_thumbnail_url(video_id, quality)
    
    # Generate all quality variants
    thumbnails = {
        "maxresdefault": screenshot_service.generate_youtube_thumbnail_url(video_id, "maxresdefault"),
        "hqdefault": screenshot_service.generate_youtube_thumbnail_url(video_id, "hqdefault"),
        "mqdefault": screenshot_service.generate_youtube_thumbnail_url(video_id, "mqdefault"),
        "sddefault": screenshot_service.generate_youtube_thumbnail_url(video_id, "sddefault"),
    }
    
    return ThumbnailResponse(
        success=True,
        video_id=video_id,
        thumbnail_url=thumbnail_url,
        thumbnails=thumbnails
    )


@router.post("/api/upload", response_model=CloudUploadResponse)
async def upload_to_cloud(request: CloudUploadRequest):
    """
    Upload clip to GoFile.io cloud storage.
    """
    file_path = settings.TEMP_DIR / request.session_id / "output.mp4"
    
    if not file_path.exists():
        return CloudUploadResponse(
            success=False,
            error="File tidak ditemukan atau sudah kadaluwarsa"
        )
    
    result = await cloud_upload_service.upload_to_gofile(
        str(file_path),
        f"clip_{request.session_id}.mp4"
    )
    return CloudUploadResponse(**result)


@router.get("/api/metadata/{video_id}", response_model=VideoMetadataResponse)
async def get_video_metadata(video_id: str):
    """
    Get additional metadata for a YouTube video.
    """
    result = await video_metadata_service.get_youtube_metadata(video_id)
    return VideoMetadataResponse(**result)


@router.get("/api/stats/{session_id}", response_model=ClipStatsResponse)
async def get_clip_stats(session_id: str):
    """
    Get statistics for a processed clip.
    """
    file_path = settings.TEMP_DIR / session_id / "output.mp4"
    
    if not file_path.exists():
        raise HTTPException(status_code=404, detail="Clip tidak ditemukan")
    
    file_size = file_path.stat().st_size
    
    # Calculate clip duration from filename if available
    # For now, return basic stats
    return ClipStatsResponse(
        success=True,
        session_id=session_id,
        clip_duration=0,  # Would need to extract from video metadata
        clip_size=file_size,
        created_at=datetime.fromtimestamp(file_path.stat().st_mtime).isoformat(),
        file_path=str(file_path)
    )