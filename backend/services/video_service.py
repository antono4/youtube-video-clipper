"""
Video processing service using yt-dlp and FFmpeg.
"""
import os
import subprocess
import uuid
from pathlib import Path
from typing import Tuple
import logging

import yt_dlp

from backend.core.config import settings
from backend.core.exceptions import VideoProcessingError, FFmpegError

logger = logging.getLogger(__name__)


class VideoService:
    """Service for video processing operations."""
    
    def __init__(self):
        self.temp_dir = settings.TEMP_DIR
        self.temp_dir.mkdir(parents=True, exist_ok=True)
    
    def create_session(self) -> str:
        """Create a new processing session."""
        session_id = str(uuid.uuid4())
        session_dir = self.temp_dir / session_id
        session_dir.mkdir(parents=True, exist_ok=True)
        return session_id
    
    def get_video_info(self, url: str) -> dict:
        """Get video information without downloading."""
        ydl_opts = {
            'no_warnings': True,
            'quiet': True,
            'extract_flat': False,
        }
        
        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(url, download=False)
                
                return {
                    'video_id': info.get('id', ''),
                    'title': info.get('title', 'Unknown'),
                    'duration': info.get('duration', 0),
                    'thumbnail': info.get('thumbnail', ''),
                    'uploader': info.get('uploader', 'Unknown'),
                    'description': info.get('description', '')[:500],
                }
        except yt_dlp.utils.DownloadError as e:
            error_msg = str(e).lower()
            if 'private' in error_msg:
                raise VideoProcessingError("Video ini bersifat private dan tidak dapat diakses.")
            elif 'blocked' in error_msg:
                raise VideoProcessingError("Video ini diblokir di wilayah Anda.")
            else:
                raise VideoProcessingError(f"Gagal mengambil info video: {str(e)}")
        except Exception as e:
            raise VideoProcessingError(f"Terjadi kesalahan: {str(e)}")
    
    def process_clip(
        self, 
        url: str, 
        start_time: int, 
        end_time: int,
        session_id: str
    ) -> Tuple[str, int]:
        """
        Process video clip using FFmpeg with streaming support.
        
        This method uses FFmpeg's ability to seek to specific timestamps
        without downloading the entire video file first.
        """
        session_dir = self.temp_dir / session_id
        output_path = session_dir / "output.mp4"
        
        # Calculate clip duration
        clip_duration = end_time - start_time
        
        # Validate duration
        if clip_duration > settings.MAX_CLIP_DURATION:
            raise VideoProcessingError(
                f"Durasi klip ({clip_duration}s) melebihi batas maksimal "
                f"({settings.MAX_CLIP_DURATION}s)"
            )
        
        try:
            # Step 1: Download video using yt-dlp (will use best stream)
            logger.info(f"Starting download for session {session_id}")
            
            ydl_opts = {
                'format': 'best[ext=mp4]/best',
                'outtmpl': str(session_dir / 'video.%(ext)s'),
                'no_warnings': True,
                'quiet': True,
            }
            
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                ydl.download([url])
            
            # Find the downloaded video file
            video_files = list(session_dir.glob('video.*'))
            if not video_files:
                raise VideoProcessingError("Gagal mengunduh video")
            
            input_video = str(video_files[0])
            
            # Step 2: Extract clip using FFmpeg
            logger.info(f"Extracting clip from {start_time}s to {end_time}s")
            
            ffmpeg_cmd = [
                'ffmpeg',
                '-y',  # Overwrite output
                '-ss', str(start_time),  # Start time
                '-i', input_video,  # Input file
                '-t', str(clip_duration),  # Duration
                '-c:v', settings.VIDEO_CODEC,  # Video codec
                '-c:a', settings.AUDIO_CODEC,  # Audio codec
                '-b:a', settings.AUDIO_BITRATE,  # Audio bitrate
                '-preset', 'fast',  # Encoding speed
                '-crf', '23',  # Quality setting
                str(output_path)
            ]
            
            result = subprocess.run(
                ffmpeg_cmd,
                capture_output=True,
                text=True,
                check=True
            )
            
            # Verify output file exists
            if not output_path.exists():
                raise FFmpegError("FFmpeg gagal membuat file output")
            
            file_size = output_path.stat().st_size
            
            # Cleanup source video (keep only output)
            if input_video != str(output_path) and os.path.exists(input_video):
                os.remove(input_video)
            
            logger.info(f"Clip created successfully: {output_path}")
            return str(output_path), file_size
            
        except subprocess.CalledProcessError as e:
            logger.error(f"FFmpeg error: {e.stderr}")
            raise FFmpegError(f"Gagal memproses video: {e.stderr}")
        except Exception as e:
            logger.error(f"Processing error: {e}")
            raise VideoProcessingError(f"Terjadi kesalahan saat memproses: {str(e)}")
    
    def cleanup_session(self, session_id: str) -> None:
        """Remove session files."""
        import shutil
        session_dir = self.temp_dir / session_id
        if session_dir.exists():
            shutil.rmtree(session_dir)
            logger.info(f"Cleaned up session: {session_id}")


# Singleton instance
video_service = VideoService()