"""
Custom exceptions for the YouTube Video Clipper application.
"""


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