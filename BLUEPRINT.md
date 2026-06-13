# 🎬 YouTube Video Clipper
## Blueprint Arsitektur & Panduan Implementasi

---

## 1. Gambaran Umum Proyek

**YouTube Video Clipper** adalah aplikasi web yang memungkinkan pengguna untuk:
- Mendownload video YouTube berdasarkan URL
- Memilih segmen waktu tertentu (start & end time)
- Memotong (clip) video secara efisien menggunakan teknik streaming
- Mengunduh hasil potongan dalam format MP4

### Tech Stack
| Layer | Teknologi | Alasan |
|-------|-----------|--------|
| **Backend** | Python 3.10+ (FastAPI) | Ekosistem video yang kuat, async support |
| **Frontend** | HTML5, Tailwind CSS, Vanilla JS | Ringan, responsif, tanpa build complex |
| **Video Processing** | yt-dlp + FFmpeg | Standar industri untuk video processing |
| **Server** | Uvicorn (ASGI) | High-performance async server |

---

## 2. Arsitektur Sistem

```
┌─────────────────────────────────────────────────────────────────┐
│                        USER INTERFACE                           │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │  URL Input → Video Preview → Timeline Selector          │   │
│  │  → Clip Processing → Download MP4                       │   │
│  └─────────────────────────────────────────────────────────┘   │
└─────────────────────────┬───────────────────────────────────────┘
                          │ HTTP/REST API
                          ▼
┌─────────────────────────────────────────────────────────────────┐
│                      FASTAPI BACKEND                            │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐       │
│  │ /api/    │  │ /api/    │  │ /api/    │  │ /api/    │       │
│  │ validate │  │ info     │  │ process  │  │ download │       │
│  └──────────┘  └──────────┘  └──────────┘  └──────────┘       │
│                                                                 │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │              VIDEO PROCESSING SERVICE                    │   │
│  │         yt-dlp (download) + FFmpeg (clip)               │   │
│  └─────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────┘
                          │
                          ▼
┌─────────────────────────────────────────────────────────────────┐
│                    FILE SYSTEM / TEMP STORAGE                   │
│         /tmp/youtube-clipper/{session_id}/output.mp4           │
└─────────────────────────────────────────────────────────────────┘
```

---

## 3. Struktur Direktori Proyek

```
youtube-clipper/
│
├── 📁 backend/                      # FastAPI Backend
│   ├── 📄 main.py                   # Entry point, FastAPI app
│   ├── 📄 requirements.txt          # Python dependencies
│   ├── 📁 api/                      # API Routes
│   │   ├── __init__.py
│   │   ├── routes.py                # API endpoint definitions
│   │   └── schemas.py               # Pydantic models
│   ├── 📁 core/                     # Core Configuration
│   │   ├── __init__.py
│   │   ├── config.py                # App settings
│   │   └── exceptions.py            # Custom exceptions
│   ├── 📁 services/                 # Business Logic
│   │   ├── __init__.py
│   │   ├── video_service.py         # Video processing logic
│   │   └── download_service.py      # YouTube download logic
│   └── 📁 utils/                    # Utilities
│       ├── __init__.py
│       └── helpers.py               # Helper functions
│
├── 📁 frontend/                     # Frontend Files
│   ├── 📄 index.html                # Main HTML file
│   ├── 📄 result.html               # Result/download page
│   ├── 📁 css/
│   │   └── styles.css               # Custom styles (besides Tailwind)
│   ├── 📁 js/
│   │   ├── app.js                   # Main application logic
│   │   ├── video-player.js          # Video player controller
│   │   ├── timeline.js              # Timeline/slider logic
│   │   └── api.js                   # API communication
│   └── 📁 assets/
│       └── logo.svg                 # App logo
│
├── 📁 temp/                         # Temporary file storage
│   └── .gitkeep                     # Keep directory
│
├── 📄 README.md                     # Project documentation
├── 📄 Dockerfile                    # Container configuration
├── 📄 docker-compose.yml            # Multi-container setup
└── 📄 .env.example                  # Environment template
```

---

## 4. Fitur Utama

### 4.1 Input URL YouTube
- Kolom teks dengan validasi real-time
- Mendukung berbagai format URL YouTube:
  - `https://www.youtube.com/watch?v=VIDEO_ID`
  - `https://youtu.be/VIDEO_ID`
  - `https://www.youtube.com/embed/VIDEO_ID`
  - `https://www.youtube.com/shorts/VIDEO_ID`

### 4.2 Video Preview
- Embed video player menggunakan YouTube IFrame API
- Menampilkan metadata video (judul, durasi, thumbnail)
- Sinkronisasi dengan timeline selector

### 4.3 Timeline Clipper
- Dual-handle range slider untuk start/end time
- Input manual format HH:MM:SS
- Visual feedback durasi klip
- Batasan maksimal 5 menit per klip

### 4.4 Processing & Clipping
- Stream-based processing (tidak perlu download full video)
- FFmpeg seeking untuk efisiensi bandwidth
- Progress indicator selama processing
- Cleanup otomatis file temporary

### 4.5 Download
- Langsung download ke perangkat user
- Format output: MP4 (H.264 + AAC)
- Naming convention: `{video_title}_{start}_{end}.mp4`

---

## 5. Detail Implementasi Kode

### 5.1 Backend - Core Configuration

```python
# backend/core/config.py
from pydantic_settings import BaseSettings
from pathlib import Path
import os

class Settings(BaseSettings):
    """Application configuration settings."""
    
    # App settings
    APP_NAME: str = "YouTube Video Clipper"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = True
    
    # File settings
    TEMP_DIR: Path = Path("/tmp/youtube-clipper")
    MAX_CLIP_DURATION: int = 300  # 5 minutes in seconds
    MAX_FILE_SIZE: int = 500 * 1024 * 1024  # 500MB
    
    # Video settings
    OUTPUT_FORMAT: str = "mp4"
    VIDEO_CODEC: str = "libx264"
    AUDIO_CODEC: str = "aac"
    AUDIO_BITRATE: str = "128k"
    
    # CORS settings
    CORS_ORIGINS: list = ["*"]
    
    class Config:
        env_file = ".env"
        case_sensitive = True

settings = Settings()

# Ensure temp directory exists
settings.TEMP_DIR.mkdir(parents=True, exist_ok=True)
```

### 5.2 Backend - API Schemas

```python
# backend/api/schemas.py
from pydantic import BaseModel, Field, field_validator
from typing import Optional
from datetime import time

class URLValidationRequest(BaseModel):
    """Request model for URL validation."""
    url: str = Field(..., description="YouTube video URL")
    
    @field_validator('url')
    @classmethod
    def validate_youtube_url(cls, v: str) -> str:
        """Validate YouTube URL format."""
        import re
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
    
    @field_validator('end_time')
    @classmethod
    def validate_max_duration(cls, v: int, info) -> int:
        """Validate clip doesn't exceed max duration."""
        from backend.core.config import settings
        if 'start_time' in info.data:
            duration = v - info.data['start_time']
            if duration > settings.MAX_CLIP_DURATION:
                raise ValueError(f'Clip duration exceeds maximum of {settings.MAX_CLIP_DURATION} seconds')
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
```

### 5.3 Backend - Video Service

```python
# backend/services/video_service.py
import os
import subprocess
import uuid
from pathlib import Path
from typing import Optional, Tuple
import logging

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
    
    def get_video_stream_url(self, url: str) -> str:
        """Extract direct stream URL from YouTube video."""
        import yt_dlp
        
        ydl_opts = {
            'format': 'best[ext=mp4]/best',
            'geturl': True,
            'no_warnings': True,
            'quiet': True,
        }
        
        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(url, download=False)
                return info.get('url', '')
        except Exception as e:
            logger.error(f"Failed to extract stream URL: {e}")
            raise VideoProcessingError(f"Failed to access video: {str(e)}")
    
    def get_video_info(self, url: str) -> dict:
        """Get video information without downloading."""
        import yt_dlp
        
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
            if 'private' in str(e).lower():
                raise VideoProcessingError("Video ini bersifat private dan tidak dapat diakses.")
            elif 'blocked' in str(e).lower():
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
        import yt_dlp
        from moviepy.editor import VideoFileClip
        
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
            if input_video != str(output_path):
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

video_service = VideoService()
```

### 5.4 Backend - API Routes

```python
# backend/api/routes.py
from fastapi import APIRouter, UploadFile, File, HTTPException, BackgroundTasks
from fastapi.responses import FileResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
import os

from backend.api.schemas import (
    URLValidationRequest,
    VideoInfoResponse,
    ClipRequest,
    ClipResponse,
    ProcessingStatusResponse
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
        return JSONResponse(content=info)
    except VideoProcessingError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal error: {str(e)}")

@router.post("/api/process", response_model=ClipResponse)
async def process_clip(request: ClipRequest, background_tasks: BackgroundTasks):
    """
    Process video clip from YouTube URL.
    """
    try:
        # Validate clip duration
        clip_duration = request.end_time - request.start_time
        if clip_duration > settings.MAX_CLIP_DURATION:
            return ClipResponse(
                success=False,
                message=f"Durasi klip maksimal adalah {settings.MAX_CLIP_DURATION // 60} menit"
            )
        
        if clip_duration <= 0:
            return ClipResponse(
                success=False,
                message="Waktu selesai harus lebih besar dari waktu mulai"
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
```

### 5.5 Backend - Main Application

```python
# backend/main.py
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import logging

from backend.core.config import settings
from backend.api.routes import router

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Create FastAPI app
app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="YouTube Video Clipper - Extract and download video clips"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routes
app.include_router(router)

@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "name": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "status": "running"
    }

@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
```

### 5.6 Frontend - HTML Structure

```html
<!-- frontend/index.html -->
<!DOCTYPE html>
<html lang="id" class="scroll-smooth">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>YouTube Video Clipper | Extract & Download Video Clips</title>
    
    <!-- Tailwind CSS -->
    <script src="https://cdn.tailwindcss.com"></script>
    
    <!-- Google Fonts -->
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@400;500;600;700&family=JetBrains+Mono:wght@400;500&display=swap" rel="stylesheet">
    
    <!-- Custom Styles -->
    <link rel="stylesheet" href="css/styles.css">
</head>
<body class="bg-neutral-950 text-white font-sans antialiased min-h-screen">
    
    <!-- Background Effects -->
    <div class="fixed inset-0 -z-10">
        <div class="absolute top-0 left-1/4 w-96 h-96 bg-red-500/20 rounded-full blur-[128px]"></div>
        <div class="absolute bottom-0 right-1/4 w-96 h-96 bg-purple-500/20 rounded-full blur-[128px]"></div>
        <div class="absolute inset-0 bg-[radial-gradient(ellipse_at_center,_var(--tw-gradient-stops))] from-neutral-900 via-neutral-950 to-black"></div>
    </div>

    <!-- Main Container -->
    <div class="max-w-6xl mx-auto px-6 py-12">
        
        <!-- Header -->
        <header class="text-center mb-16">
            <div class="inline-flex items-center gap-3 mb-6">
                <svg class="w-12 h-12 text-red-500" viewBox="0 0 24 24" fill="currentColor">
                    <path d="M19.615 3.184c-3.604-.246-11.631-.245-15.23 0C.488 3.45.029 5.804 0 12c.029 6.185.484 8.549 4.385 8.816 3.6.245 11.626.246 15.23 0C23.512 20.55 23.971 18.196 24 12c-.029-6.185-.484-8.549-4.385-8.816zM9 16V8l8 3.993L9 16z"/>
                </svg>
                <h1 class="text-5xl font-bold tracking-tight">
                    <span class="bg-gradient-to-r from-red-400 to-red-600 bg-clip-text text-transparent">
                        YouTube
                    </span>
                    <span class="text-white">Clipper</span>
                </h1>
            </div>
            <p class="text-neutral-400 text-lg max-w-xl mx-auto">
                Extract dan unduh bagian spesifik dari video YouTube dalam hitungan menit. 
                Tanpa software tambahan, langsung dari browser.
            </p>
        </header>

        <!-- Main Content -->
        <main class="space-y-8">
            
            <!-- URL Input Section -->
            <section class="bg-neutral-900/50 backdrop-blur-xl border border-neutral-800 rounded-2xl p-8">
                <div class="flex flex-col md:flex-row gap-4">
                    <div class="flex-1 relative">
                        <div class="absolute inset-y-0 left-0 pl-4 flex items-center pointer-events-none">
                            <svg class="w-5 h-5 text-neutral-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13.828 10.172a4 4 0 00-5.656 0l-4 4a4 4 0 105.656 5.656l1.102-1.101m-.758-4.899a4 4 0 005.656 0l4-4a4 4 0 00-5.656-5.656l-1.1 1.1"/>
                            </svg>
                        </div>
                        <input 
                            type="url" 
                            id="videoUrl" 
                            placeholder="Tempelkan URL YouTube di sini..."
                            class="w-full pl-12 pr-4 py-4 bg-neutral-800 border border-neutral-700 rounded-xl text-white placeholder-neutral-500 focus:outline-none focus:ring-2 focus:ring-red-500 focus:border-transparent transition-all"
                        >
                    </div>
                    <button 
                        id="validateBtn"
                        class="px-8 py-4 bg-red-600 hover:bg-red-700 text-white font-semibold rounded-xl transition-all flex items-center justify-center gap-2 disabled:opacity-50 disabled:cursor-not-allowed"
                    >
                        <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z"/>
                        </svg>
                        Validasi
                    </button>
                </div>
                
                <!-- Validation Status -->
                <div id="validationStatus" class="mt-4 hidden">
                    <div class="flex items-center gap-3 text-sm">
                        <div class="w-2 h-2 rounded-full bg-yellow-500 animate-pulse"></div>
                        <span id="statusText" class="text-neutral-400">Memvalidasi URL...</span>
                    </div>
                </div>
            </section>

            <!-- Video Preview Section -->
            <section id="previewSection" class="bg-neutral-900/50 backdrop-blur-xl border border-neutral-800 rounded-2xl p-8 hidden">
                <div class="flex flex-col lg:flex-row gap-8">
                    
                    <!-- Video Player -->
                    <div class="flex-1">
                        <div class="aspect-video bg-black rounded-xl overflow-hidden">
                            <div id="playerContainer" class="w-full h-full flex items-center justify-center">
                                <div class="text-neutral-500 text-center">
                                    <svg class="w-16 h-16 mx-auto mb-2 opacity-50" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M14.752 11.168l-3.197-2.132A1 1 0 0010 9.87v4.263a1 1 0 001.555.832l3.197-2.132a1 1 0 000-1.664z"/>
                                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 12a9 9 0 11-18 0 9 9 0 0118 0z"/>
                                    </svg>
                                    <p>Video preview</p>
                                </div>
                            </div>
                        </div>
                        
                        <!-- Video Info -->
                        <div class="mt-4">
                            <h2 id="videoTitle" class="text-xl font-semibold text-white mb-2">Loading...</h2>
                            <div class="flex flex-wrap items-center gap-4 text-sm text-neutral-400">
                                <span id="videoUploader" class="flex items-center gap-1">
                                    <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z"/>
                                    </svg>
                                    <span>Loading...</span>
                                </span>
                                <span id="videoDuration" class="flex items-center gap-1">
                                    <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z"/>
                                    </svg>
                                    <span>00:00</span>
                                </span>
                            </div>
                        </div>
                    </div>

                    <!-- Clip Controls -->
                    <div class="lg:w-96 space-y-6">
                        
                        <!-- Timeline Selector -->
                        <div class="bg-neutral-800/50 rounded-xl p-6">
                            <h3 class="text-sm font-semibold text-neutral-300 mb-4 uppercase tracking-wider">
                                Pilih Segment Waktu
                            </h3>
                            
                            <!-- Time Inputs -->
                            <div class="grid grid-cols-2 gap-4 mb-6">
                                <div>
                                    <label class="block text-xs text-neutral-500 mb-2">Waktu Mulai</label>
                                    <input 
                                        type="text" 
                                        id="startTime" 
                                        value="00:00:00"
                                        placeholder="00:00:00"
                                        class="w-full px-4 py-3 bg-neutral-900 border border-neutral-700 rounded-lg text-white font-mono text-center focus:outline-none focus:ring-2 focus:ring-red-500"
                                    >
                                </div>
                                <div>
                                    <label class="block text-xs text-neutral-500 mb-2">Waktu Selesai</label>
                                    <input 
                                        type="text" 
                                        id="endTime" 
                                        value="00:00:30"
                                        placeholder="00:00:30"
                                        class="w-full px-4 py-3 bg-neutral-900 border border-neutral-700 rounded-lg text-white font-mono text-center focus:outline-none focus:ring-2 focus:ring-red-500"
                                    >
                                </div>
                            </div>
                            
                            <!-- Range Slider -->
                            <div class="space-y-4">
                                <div class="relative pt-2">
                                    <input 
                                        type="range" 
                                        id="startSlider" 
                                        min="0" 
                                        max="100" 
                                        value="0"
                                        class="timeline-slider w-full h-2 bg-neutral-700 rounded-lg appearance-none cursor-pointer accent-red-500"
                                    >
                                    <input 
                                        type="range" 
                                        id="endSlider" 
                                        min="0" 
                                        max="100" 
                                        value="10"
                                        class="timeline-slider w-full h-2 bg-neutral-700 rounded-lg appearance-none cursor-pointer accent-red-500 absolute top-2 left-0 pointer-events-none"
                                        style="background: transparent;"
                                    >
                                </div>
                                
                                <!-- Duration Display -->
                                <div class="flex justify-between items-center text-sm">
                                    <span id="clipDuration" class="text-neutral-400">
                                        Durasi: <span class="text-white font-semibold">30 detik</span>
                                    </span>
                                    <span id="maxDurationWarning" class="text-amber-500 hidden">
                                        ⚠️ Maks 5 menit
                                    </span>
                                </div>
                            </div>
                        </div>
                        
                        <!-- Process Button -->
                        <button 
                            id="processBtn"
                            class="w-full py-4 bg-gradient-to-r from-red-600 to-red-700 hover:from-red-500 hover:to-red-600 text-white font-bold rounded-xl transition-all transform hover:scale-[1.02] active:scale-[0.98] disabled:opacity-50 disabled:cursor-not-allowed disabled:transform-none flex items-center justify-center gap-3"
                        >
                            <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M14.752 11.168l-3.197-2.132A1 1 0 0010 9.87v4.263a1 1 0 001.555.832l3.197-2.132a1 1 0 000-1.664z"/>
                                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 12a9 9 0 11-18 0 9 9 0 0118 0z"/>
                            </svg>
                            Generate Clip
                        </button>
                        
                        <!-- Progress Bar -->
                        <div id="progressContainer" class="hidden">
                            <div class="relative pt-1">
                                <div class="flex mb-2 items-center justify-between">
                                    <div>
                                        <span class="text-xs font-semibold inline-block text-red-500">
                                            Processing
                                        </span>
                                    </div>
                                    <div class="text-right">
                                        <span id="progressPercent" class="text-xs font-semibold inline-block text-red-500">
                                            0%
                                        </span>
                                    </div>
                                </div>
                                <div class="overflow-hidden h-2 mb-4 text-xs flex rounded bg-neutral-800">
                                    <div id="progressBar" style="width:0%" class="shadow-none flex flex-col text-center whitespace-nowrap text-white justify-center bg-gradient-to-r from-red-600 to-red-500 transition-all duration-300"></div>
                                </div>
                                <p id="progressMessage" class="text-xs text-neutral-500 text-center">Memproses video...</p>
                            </div>
                        </div>
                    </div>
                </div>
            </section>

            <!-- Result Section -->
            <section id="resultSection" class="bg-neutral-900/50 backdrop-blur-xl border border-neutral-800 rounded-2xl p-8 hidden">
                <div class="text-center py-8">
                    <div class="w-20 h-20 mx-auto mb-6 bg-green-500/20 rounded-full flex items-center justify-center">
                        <svg class="w-10 h-10 text-green-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7"/>
                        </svg>
                    </div>
                    <h2 class="text-2xl font-bold text-white mb-2">Clip Berhasil Dibuat!</h2>
                    <p id="resultInfo" class="text-neutral-400 mb-6">File siap diunduh</p>
                    
                    <a 
                        id="downloadBtn"
                        href="#"
                        download
                        class="inline-flex items-center gap-3 px-8 py-4 bg-green-600 hover:bg-green-700 text-white font-semibold rounded-xl transition-all"
                    >
                        <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-4l-4 4m0 0l-4-4m4 4V4"/>
                        </svg>
                        Download MP4
                    </a>
                </div>
            </section>

        </main>

        <!-- Footer -->
        <footer class="mt-16 text-center text-neutral-500 text-sm">
            <p>YouTube Video Clipper • Built with FastAPI & Tailwind CSS</p>
            <p class="mt-1">Gunakan secara bertanggung jawab dan patuhi Terms of Service YouTube.</p>
        </footer>
    </div>

    <!-- Scripts -->
    <script src="js/api.js"></script>
    <script src="js/video-player.js"></script>
    <script src="js/timeline.js"></script>
    <script src="js/app.js"></script>
</body>
</html>
```

### 5.7 Frontend - JavaScript Logic

```javascript
// frontend/js/app.js
/**
 * YouTube Video Clipper - Main Application Logic
 */

class YouTubeClipper {
    constructor() {
        this.api = new ClipperAPI();
        this.videoId = null;
        this.videoDuration = 0;
        this.startTime = 0;
        this.endTime = 30;
        
        this.initElements();
        this.bindEvents();
    }
    
    initElements() {
        // Input elements
        this.urlInput = document.getElementById('videoUrl');
        this.validateBtn = document.getElementById('validateBtn');
        this.validationStatus = document.getElementById('validationStatus');
        this.statusText = document.getElementById('statusText');
        
        // Preview elements
        this.previewSection = document.getElementById('previewSection');
        this.playerContainer = document.getElementById('playerContainer');
        this.videoTitle = document.getElementById('videoTitle');
        this.videoUploader = document.getElementById('videoUploader').querySelector('span');
        this.videoDurationEl = document.getElementById('videoDuration').querySelector('span');
        
        // Timeline elements
        this.startTimeInput = document.getElementById('startTime');
        this.endTimeInput = document.getElementById('endTime');
        this.startSlider = document.getElementById('startSlider');
        this.endSlider = document.getElementById('endSlider');
        this.clipDuration = document.getElementById('clipDuration');
        this.maxDurationWarning = document.getElementById('maxDurationWarning');
        
        // Process elements
        this.processBtn = document.getElementById('processBtn');
        this.progressContainer = document.getElementById('progressContainer');
        this.progressBar = document.getElementById('progressBar');
        this.progressPercent = document.getElementById('progressPercent');
        this.progressMessage = document.getElementById('progressMessage');
        
        // Result elements
        this.resultSection = document.getElementById('resultSection');
        this.downloadBtn = document.getElementById('downloadBtn');
        this.resultInfo = document.getElementById('resultInfo');
    }
    
    bindEvents() {
        // URL validation
        this.validateBtn.addEventListener('click', () => this.validateURL());
        this.urlInput.addEventListener('keypress', (e) => {
            if (e.key === 'Enter') this.validateURL();
        });
        
        // Timeline controls
        this.startSlider.addEventListener('input', (e) => this.handleSliderChange('start', e.target.value));
        this.endSlider.addEventListener('input', (e) => this.handleSliderChange('end', e.target.value));
        this.startTimeInput.addEventListener('change', (e) => this.handleTimeInput('start', e.target.value));
        this.endTimeInput.addEventListener('change', (e) => this.handleTimeInput('end', e.target.value));
        
        // Process clip
        this.processBtn.addEventListener('click', () => this.processClip());
        
        // Download
        this.downloadBtn.addEventListener('click', () => this.downloadClip());
    }
    
    showStatus(message, type = 'info') {
        this.validationStatus.classList.remove('hidden');
        const dot = this.validationStatus.querySelector('.w-2');
        dot.className = `w-2 h-2 rounded-full ${type === 'success' ? 'bg-green-500' : type === 'error' ? 'bg-red-500' : 'bg-yellow-500'} animate-pulse`;
        this.statusText.textContent = message;
    }
    
    hideStatus() {
        this.validationStatus.classList.add('hidden');
    }
    
    async validateURL() {
        const url = this.urlInput.value.trim();
        
        if (!url) {
            this.showStatus('Masukkan URL YouTube terlebih dahulu', 'error');
            return;
        }
        
        this.validateBtn.disabled = true;
        this.showStatus('Memvalidasi URL...');
        
        try {
            const response = await this.api.validateURL(url);
            this.videoId = response.video_id;
            this.videoDuration = response.duration;
            
            // Update UI
            this.videoTitle.textContent = response.title;
            this.videoUploader.textContent = response.uploader;
            this.videoDurationEl.textContent = this.formatTime(response.duration);
            
            // Initialize player
            this.initPlayer(response);
            
            // Show preview section
            this.previewSection.classList.remove('hidden');
            this.hideStatus();
            
            // Initialize sliders
            this.initSliders();
            
            // Scroll to preview
            this.previewSection.scrollIntoView({ behavior: 'smooth', block: 'start' });
            
        } catch (error) {
            this.showStatus(error.message || 'Gagal memvalidasi URL', 'error');
            this.previewSection.classList.add('hidden');
        } finally {
            this.validateBtn.disabled = false;
        }
    }
    
    initPlayer(videoInfo) {
        this.playerContainer.innerHTML = `
            <iframe 
                width="100%" 
                height="100%" 
                src="https://www.youtube.com/embed/${videoInfo.video_id}?enablejsapi=1" 
                frameborder="0" 
                allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture" 
                allowfullscreen>
            </iframe>
        `;
    }
    
    initSliders() {
        this.startSlider.max = this.videoDuration;
        this.endSlider.max = this.videoDuration;
        this.startSlider.value = 0;
        this.endSlider.value = Math.min(30, this.videoDuration);
        
        this.startTime = 0;
        this.endTime = Math.min(30, this.videoDuration);
        
        this.updateTimeDisplays();
    }
    
    handleSliderChange(type, value) {
        const seconds = parseInt(value);
        
        if (type === 'start') {
            this.startTime = Math.min(seconds, this.endTime - 1);
            this.startSlider.value = this.startTime;
        } else {
            this.endTime = Math.max(seconds, this.startTime + 1);
            this.endSlider.value = this.endTime;
        }
        
        this.updateTimeDisplays();
    }
    
    handleTimeInput(type, value) {
        const seconds = this.parseTime(value);
        
        if (seconds === null) return;
        
        if (type === 'start') {
            if (seconds >= this.endTime) {
                this.showStatus('Waktu mulai harus lebih kecil dari waktu selesai', 'error');
                return;
            }
            this.startTime = seconds;
            this.startSlider.value = seconds;
        } else {
            if (seconds <= this.startTime) {
                this.showStatus('Waktu selesai harus lebih besar dari waktu mulai', 'error');
                return;
            }
            this.endTime = seconds;
            this.endSlider.value = seconds;
        }
        
        this.updateTimeDisplays();
        this.hideStatus();
    }
    
    updateTimeDisplays() {
        this.startTimeInput.value = this.formatTime(this.startTime);
        this.endTimeInput.value = this.formatTime(this.endTime);
        
        const duration = this.endTime - this.startTime;
        this.clipDuration.innerHTML = `Durasi: <span class="text-white font-semibold">${this.formatDuration(duration)}</span>`;
        
        // Show warning if exceeds 5 minutes
        if (duration > 300) {
            this.maxDurationWarning.classList.remove('hidden');
            this.processBtn.disabled = true;
        } else {
            this.maxDurationWarning.classList.add('hidden');
            this.processBtn.disabled = false;
        }
    }
    
    async processClip() {
        const url = this.urlInput.value.trim();
        
        // Show progress
        this.progressContainer.classList.remove('hidden');
        this.processBtn.disabled = true;
        this.updateProgress(0, 'Menghubungi server...');
        
        try {
            // Simulate progress for better UX
            this.simulateProgress(30, 'Memproses video...');
            
            const response = await this.api.processClip(url, this.startTime, this.endTime);
            
            if (response.success) {
                this.updateProgress(100, 'Selesai!');
                
                // Update download button
                this.downloadBtn.href = response.file_path;
                this.downloadBtn.download = `clip_${this.startTime}_${this.endTime}.mp4`;
                this.resultInfo.textContent = `Clip ${this.formatTime(this.startTime)} - ${this.formatTime(this.endTime)} (${this.formatFileSize(response.file_size)})`;
                
                // Show result section
                setTimeout(() => {
                    this.progressContainer.classList.add('hidden');
                    this.resultSection.classList.remove('hidden');
                    this.resultSection.scrollIntoView({ behavior: 'smooth', block: 'start' });
                }, 500);
            } else {
                throw new Error(response.message);
            }
            
        } catch (error) {
            this.showStatus(error.message || 'Gagal memproses video', 'error');
            this.progressContainer.classList.add('hidden');
        } finally {
            this.processBtn.disabled = false;
        }
    }
    
    simulateProgress(target, message) {
        let progress = 0;
        const interval = setInterval(() => {
            progress += Math.random() * 15;
            if (progress >= target) {
                progress = target;
                clearInterval(interval);
            }
            this.updateProgress(progress, message);
        }, 500);
    }
    
    updateProgress(percent, message) {
        this.progressBar.style.width = `${percent}%`;
        this.progressPercent.textContent = `${Math.round(percent)}%`;
        this.progressMessage.textContent = message;
    }
    
    downloadClip() {
        // Download is handled by the href attribute
        console.log('Download started');
    }
    
    // Utility functions
    formatTime(seconds) {
        const h = Math.floor(seconds / 3600);
        const m = Math.floor((seconds % 3600) / 60);
        const s = seconds % 60;
        return `${h.toString().padStart(2, '0')}:${m.toString().padStart(2, '0')}:${s.toString().padStart(2, '0')}`;
    }
    
    parseTime(timeStr) {
        const parts = timeStr.split(':').map(Number);
        if (parts.some(isNaN)) return null;
        
        if (parts.length === 3) {
            return parts[0] * 3600 + parts[1] * 60 + parts[2];
        } else if (parts.length === 2) {
            return parts[0] * 60 + parts[1];
        }
        return null;
    }
    
    formatDuration(seconds) {
        if (seconds < 60) return `${seconds} detik`;
        const m = Math.floor(seconds / 60);
        const s = seconds % 60;
        return s > 0 ? `${m} menit ${s} detik` : `${m} menit`;
    }
    
    formatFileSize(bytes) {
        if (bytes < 1024) return `${bytes} B`;
        if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)} KB`;
        return `${(bytes / (1024 * 1024)).toFixed(1)} MB`;
    }
}

// Initialize app when DOM is ready
document.addEventListener('DOMContentLoaded', () => {
    window.clipper = new YouTubeClipper();
});
```

### 5.8 Frontend - API Communication

```javascript
// frontend/js/api.js
/**
 * API Communication Layer
 */

class ClipperAPI {
    constructor(baseURL = '') {
        this.baseURL = baseURL || 'http://localhost:8000';
    }
    
    async validateURL(url) {
        const response = await fetch(`${this.baseURL}/api/validate`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ url }),
        });
        
        if (!response.ok) {
            const error = await response.json();
            throw new Error(error.detail || 'Validasi gagal');
        }
        
        return response.json();
    }
    
    async processClip(url, startTime, endTime) {
        const response = await fetch(`${this.baseURL}/api/process`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                url,
                start_time: startTime,
                end_time: endTime
            }),
        });
        
        return response.json();
    }
    
    async cleanupSession(sessionId) {
        const response = await fetch(`${this.baseURL}/api/cleanup/${sessionId}`, {
            method: 'DELETE',
        });
        
        return response.json();
    }
}
```

### 5.9 Frontend - Timeline Controls

```javascript
// frontend/js/timeline.js
/**
 * Timeline Controller - Custom dual-handle slider
 */

class TimelineController {
    constructor(startSlider, endSlider, options = {}) {
        this.startSlider = startSlider;
        this.endSlider = endSlider;
        this.options = {
            min: 0,
            max: 100,
            step: 1,
            onChange: () => {},
            ...options
        };
        
        this.init();
    }
    
    init() {
        // Ensure start is always less than end
        this.startSlider.addEventListener('input', () => this.handleStartChange());
        this.endSlider.addEventListener('input', () => this.handleEndChange());
        
        // Initialize styles
        this.updateSliderStyles();
    }
    
    handleStartChange() {
        let start = parseInt(this.startSlider.value);
        let end = parseInt(this.endSlider.value);
        
        if (start >= end) {
            start = end - 1;
            this.startSlider.value = start;
        }
        
        this.updateSliderStyles();
        this.options.onChange('start', start, end);
    }
    
    handleEndChange() {
        let start = parseInt(this.startSlider.value);
        let end = parseInt(this.endSlider.value);
        
        if (end <= start) {
            end = start + 1;
            this.endSlider.value = end;
        }
        
        this.updateSliderStyles();
        this.options.onChange('end', start, end);
    }
    
    updateSliderStyles() {
        const start = parseInt(this.startSlider.value);
        const end = parseInt(this.endSlider.value);
        const range = this.options.max - this.options.min;
        
        const startPercent = ((start - this.options.min) / range) * 100;
        const endPercent = ((end - this.options.min) / range) * 100;
        
        // Create gradient background for end slider
        this.endSlider.style.background = `linear-gradient(to right, 
            #374151 0%, 
            #374151 ${startPercent}%, 
            transparent ${startPercent}%, 
            transparent ${endPercent}%, 
            #374151 ${endPercent}%, 
            #374151 100%)`;
    }
    
    setRange(min, max) {
        this.options.min = min;
        this.options.max = max;
        this.startSlider.min = min;
        this.startSlider.max = max;
        this.endSlider.min = min;
        this.endSlider.max = max;
        this.updateSliderStyles();
    }
    
    setValues(start, end) {
        this.startSlider.value = start;
        this.endSlider.value = end;
        this.updateSliderStyles();
    }
    
    getValues() {
        return {
            start: parseInt(this.startSlider.value),
            end: parseInt(this.endSlider.value)
        };
    }
}
```

---

## 6. Penanganan Error & Validasi

### 6.1 Diagram Alur Validasi

```
┌─────────────────────────────────────────────────────────────────┐
│                      VALIDATION FLOW                            │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│  1. URL VALIDATION                                              │
│     ├── Format check (regex patterns)                           │
│     ├── YouTube domain verification                             │
│     └── Video ID extraction                                     │
└─────────────────────────────────────────────────────────────────┘
                              │
              ┌───────────────┴───────────────┐
              │                               │
           ✓ Valid                          ✗ Invalid
              │                               │
              ▼                               ▼
┌─────────────────────────┐    ┌─────────────────────────────┐
│  2. VIDEO ACCESS        │    │ Error: "URL YouTube tidak   │
│     ├── Check visibility│    │ valid. Pastikan format URL  │
│     ├── Check not       │    │ benar (youtube.com/watch?   │
│       private/blocked   │    │ v=...)"                     │
│     └── Get metadata    │    └─────────────────────────────┘
└─────────────────────────┘
              │
      ┌───────┴───────┐
      │               │
   ✓ Accessible    ✗ Blocked
      │               │
      ▼               ▼
┌─────────────┐  ┌─────────────────────────────┐
│  3. TIME    │  │ Error: "Video bersifat      │
│  VALIDATION │  │ private/diblokir dan tidak  │
│     │       │  │ dapat diakses"              │
│     ▼       │  └─────────────────────────────┘
│  ┌──────────────┐
│  │ start < end  │────────────────────────────────────────┐
│  └──────────────┘                                        │
│     │                                                      │
│  ✓ Valid                                                  │
│     │                                                      │
│     ▼                                                      │
│  ┌────────────────────────────┐                           │
│  │ duration ≤ MAX_CLIP (300s) │                           │
│  └────────────────────────────┘                           │
│     │                                                      │
│  ✓ Valid                                                  │
│     │                                                      │
│     ▼                                                      │
│  ┌────────────────────────────────────────────────────────┤
│  │              ✓ READY TO PROCESS                         │
│  └────────────────────────────────────────────────────────┘
```

### 6.2 Error Handling Implementation

```python
# backend/core/exceptions.py
class VideoProcessingError(Exception):
    """Base exception for video processing errors."""
    pass

class URLValidationError(VideoProcessingError):
    """Invalid YouTube URL."""
    pass

class VideoAccessError(VideoProcessingError):
    """Cannot access video (private, blocked, etc.)."""
    pass

class InvalidTimeRangeError(VideoProcessingError):
    """Invalid start/end time values."""
    pass

class MaxDurationExceededError(VideoProcessingError):
    """Clip duration exceeds maximum allowed."""
    pass

class FFmpegError(VideoProcessingError):
    """FFmpeg processing failed."""
    pass
```

### 6.3 Validation Rules Summary

| Validation | Rule | Error Message |
|------------|------|---------------|
| URL Format | Must match YouTube URL patterns | "URL tidak valid. Gunakan format: youtube.com/watch?v=..." |
| Video Access | Video must be public/unlisted | "Video bersifat private atau diblokir" |
| Start Time | Must be ≥ 0 and < video duration | "Waktu mulai tidak valid" |
| End Time | Must be > start time and ≤ video duration | "Waktu selesai harus lebih besar dari waktu mulai" |
| Clip Duration | Must be ≤ 300 seconds (5 minutes) | "Durasi klip maksimal adalah 5 menit" |
| File Size | Must be ≤ 500MB | "File hasil terlalu besar" |

---

## 7. Panduan Instalasi & Deployment

### 7.1 Persyaratan Sistem

- **Python**: 3.10 atau lebih baru
- **FFmpeg**: Versi terbaru (untuk video processing)
- **Node.js**: 18+ (opsional, untuk development)
- **RAM**: Minimal 2GB (direkomendasikan 4GB+)
- **Storage**: Minimal 2GB free space untuk temp files

### 7.2 Instalasi di Localhost

#### Langkah 1: Clone Repository

```bash
# Clone atau download project
cd youtube-clipper

# Atau buat struktur folder manual
mkdir -p youtube-clipper && cd youtube-clipper
```

#### Langkah 2: Install FFmpeg

**macOS:**
```bash
brew install ffmpeg
```

**Ubuntu/Debian:**
```bash
sudo apt update
sudo apt install ffmpeg
```

**Windows (menggunakan Chocolatey):**
```powershell
choco install ffmpeg
```

**Windows (manual):**
1. Download dari https://ffmpeg.org/download.html
2. Ekstrak dan tambahkan ke PATH

#### Langkah 3: Buat Virtual Environment

```bash
# Buat virtual environment
python -m venv venv

# Aktifkan (macOS/Linux)
source venv/bin/activate

# Aktifkan (Windows)
venv\Scripts\activate
```

#### Langkah 4: Install Python Dependencies

```bash
# Install semua dependencies
pip install -r backend/requirements.txt
```

**Atau install manual:**
```bash
pip install fastapi uvicorn[standard] pydantic-settings yt-dlp moviepy python-multipart
```

#### Langkah 5: Jalankan Backend Server

```bash
# Masuk ke folder backend
cd backend

# Jalankan server
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

Server akan berjalan di `http://localhost:8000`

#### Langkah 6: Buka Frontend

Buka file `frontend/index.html` di browser, atau gunakan static file server:

```bash
# Install http server (one-time)
npm install -g http-server

# Jalankan di folder root project
http-server -p 3000 -c-1

# Buka http://localhost:3000/frontend/index.html
```

### 7.3 Docker Deployment (Production)

#### Dockerfile

```dockerfile
# backend/Dockerfile
FROM python:3.11-slim

# Install FFmpeg
RUN apt-get update && apt-get install -y ffmpeg && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Copy requirements
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Create temp directory
RUN mkdir -p /tmp/youtube-clipper

# Expose port
EXPOSE 8000

# Run application
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
```

#### docker-compose.yml

```yaml
version: '3.8'

services:
  clipper-backend:
    build: ./backend
    ports:
      - "8000:8000"
    volumes:
      - temp_files:/tmp/youtube-clipper
    environment:
      - DEBUG=false
      - MAX_CLIP_DURATION=300
    restart: unless-stopped

  clipper-frontend:
    image: nginx:alpine
    ports:
      - "80:80"
    volumes:
      - ./frontend:/usr/share/nginx/html:ro
      - ./nginx.conf:/etc/nginx/conf.d/default.conf:ro
    depends_on:
      - clipper-backend
    restart: unless-stopped

volumes:
  temp_files:
```

#### nginx.conf

```nginx
server {
    listen 80;
    server_name localhost;
    
    root /usr/share/nginx/html;
    index index.html;

    # Serve frontend
    location / {
        try_files $uri $uri/ /index.html;
    }

    # Proxy API requests to backend
    location /api/ {
        proxy_pass http://clipper-backend:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        
        # Allow large uploads
        client_max_body_size 500M;
        proxy_read_timeout 300s;
        proxy_connect_timeout 75s;
    }
}
```

### 7.4 Environment Variables

Buat file `.env` di folder `backend/`:

```env
# Application Settings
APP_NAME=YouTube Video Clipper
APP_VERSION=1.0.0
DEBUG=false

# File Settings
TEMP_DIR=/tmp/youtube-clipper
MAX_CLIP_DURATION=300
MAX_FILE_SIZE=524288000

# Video Settings
OUTPUT_FORMAT=mp4
VIDEO_CODEC=libx264
AUDIO_CODEC=aac
AUDIO_BITRATE=128k

# CORS Settings
CORS_ORIGINS=http://localhost:3000,http://localhost:80
```

---

## 8. Requirements.txt

```
# backend/requirements.txt
fastapi==0.109.0
uvicorn[standard]==0.27.0
pydantic-settings==2.1.0
yt-dlp==2024.1.31
moviepy==1.0.3
python-multipart==0.0.6
aiofiles==23.2.1
httpx==0.26.0
```

---

## 9. API Reference

### POST /api/validate

Validasi URL YouTube dan dapatkan informasi video.

**Request:**
```json
{
  "url": "https://www.youtube.com/watch?v=dQw4w9WgXcQ"
}
```

**Response (200 OK):**
```json
{
  "video_id": "dQw4w9WgXcQ",
  "title": "Rick Astley - Never Gonna Give You Up",
  "duration": 213,
  "thumbnail": "https://i.ytimg.com/vi/dQw4w9WgXcQ/maxresdefault.jpg",
  "uploader": "Rick Astley",
  "description": "The official video for Rick Astley..."
}
```

### POST /api/process

Proses klip video.

**Request:**
```json
{
  "url": "https://www.youtube.com/watch?v=dQw4w9WgXcQ",
  "start_time": 30,
  "end_time": 60
}
```

**Response (200 OK):**
```json
{
  "success": true,
  "message": "Clip berhasil dibuat!",
  "file_path": "/api/download/abc123-def456",
  "file_size": 5242880,
  "session_id": "abc123-def456"
}
```

### GET /api/download/{session_id}

Download file klip yang sudah diproses.

**Response:** File MP4 binary stream

### DELETE /api/cleanup/{session_id}

Hapus file session dari server.

**Response:**
```json
{
  "message": "Session cleaned up"
}
```

---

## 10. Troubleshooting

### Error Umum dan Solusi

| Error | Cause | Solution |
|-------|-------|----------|
| `ffmpeg: command not found` | FFmpeg belum terinstall | Install FFmpeg sesuai OS |
| `Video is private` | Video YouTube private | Gunakan video yang publicly available |
| `Connection timeout` | Network issues | Cek koneksi internet, coba lagi |
| `File too large` | Klip > 500MB | Kurangi durasi klip |
| `CORS error` | Frontend-backend port mismatch | Sesuaikan CORS_ORIGINS di .env |

### Performance Tips

1. **Batch Processing**: Untuk klip banyak, proses secara berurutan
2. **Cleanup**: File temp otomatis dihapus setelah download
3. **Concurrent Requests**: Batasi request simultan untuk mencegah overload
4. **CDN**: Serve file statis via CDN untuk production

---

## 11. Kesimpulan

Blueprint ini menyediakan panduan lengkap untuk membangun **YouTube Video Clipper** dengan:

✅ **Arsitektur modular** yang mudah dipelihara
✅ **Tech stack modern** (FastAPI, Tailwind CSS, yt-dlp, FFmpeg)
✅ **UI responsif** dengan desain profesional
✅ **Validasi robust** dan penanganan error komprehensif
✅ **Deployment fleksibel** (local, Docker, cloud)

Semua kode siap digunakan dan dapat langsung diimplementasikan. Untuk pertanyaan atau improvement, silakan buat issue di repository.