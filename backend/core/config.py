"""
Application configuration settings.
"""
from pydantic_settings import BaseSettings
from pathlib import Path


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