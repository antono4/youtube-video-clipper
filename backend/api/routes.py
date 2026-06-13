"""
FastAPI routes for the YouTube Video Clipper API.
"""
from fastapi import APIRouter, HTTPException
from fastapi.responses import FileResponse

from backend.api.schemas import (
    URLValidationRequest,
    VideoInfoResponse,
    ClipRequest,
    ClipResponse,
)
from backend.services.video_service import video_service
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