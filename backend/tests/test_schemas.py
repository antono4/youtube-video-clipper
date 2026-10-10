"""
Unit tests for the YouTube Video Clipper application.
"""
import pytest
from pydantic import ValidationError
from backend.api.schemas import (
    URLValidationRequest,
    ClipRequest,
    VideoInfoResponse,
    ClipResponse,
)


class TestURLValidationSchema:
    """Test URL validation schemas."""

    def test_valid_youtube_watch_url(self):
        """Test valid YouTube watch URL."""
        request = URLValidationRequest(url="https://www.youtube.com/watch?v=dQw4w9WgXcQ")
        assert request.url == "https://www.youtube.com/watch?v=dQw4w9WgXcQ"

    def test_valid_youtube_short_url(self):
        """Test valid YouTube short URL."""
        request = URLValidationRequest(url="https://youtu.be/dQw4w9WgXcQ")
        assert request.url == "https://youtu.be/dQw4w9WgXcQ"

    def test_valid_youtube_embed_url(self):
        """Test valid YouTube embed URL."""
        request = URLValidationRequest(url="https://www.youtube.com/embed/dQw4w9WgXcQ")
        assert request.url == "https://www.youtube.com/embed/dQw4w9WgXcQ"

    def test_valid_youtube_shorts_url(self):
        """Test valid YouTube shorts URL."""
        request = URLValidationRequest(url="https://www.youtube.com/shorts/dQw4w9WgXcQ")
        assert request.url == "https://www.youtube.com/shorts/dQw4w9WgXcQ"

    def test_valid_url_without_protocol(self):
        """Test valid URL without https protocol."""
        request = URLValidationRequest(url="www.youtube.com/watch?v=dQw4w9WgXcQ")
        assert request.url == "www.youtube.com/watch?v=dQw4w9WgXcQ"

    def test_invalid_url_raises_error(self):
        """Test invalid URL raises validation error."""
        with pytest.raises(ValidationError) as exc_info:
            URLValidationRequest(url="https://example.com/video")
        assert "Invalid YouTube URL format" in str(exc_info.value)

    def test_totally_invalid_url(self):
        """Test completely invalid URL."""
        with pytest.raises(ValidationError):
            URLValidationRequest(url="not a url at all")

    def test_empty_url(self):
        """Test empty URL."""
        with pytest.raises(ValidationError):
            URLValidationRequest(url="")


class TestClipRequestSchema:
    """Test clip request schemas."""

    def test_valid_clip_request(self):
        """Test valid clip request."""
        request = ClipRequest(
            url="https://www.youtube.com/watch?v=dQw4w9WgXcQ",
            start_time=10,
            end_time=60
        )
        assert request.url == "https://www.youtube.com/watch?v=dQw4w9WgXcQ"
        assert request.start_time == 10
        assert request.end_time == 60

    def test_start_time_zero(self):
        """Test start_time can be zero."""
        request = ClipRequest(
            url="https://www.youtube.com/watch?v=dQw4w9WgXcQ",
            start_time=0,
            end_time=60
        )
        assert request.start_time == 0

    def test_end_time_must_be_greater_than_start_time(self):
        """Test end_time must be greater than start_time."""
        with pytest.raises(ValidationError) as exc_info:
            ClipRequest(
                url="https://www.youtube.com/watch?v=dQw4w9WgXcQ",
                start_time=60,
                end_time=60
            )
        assert "end_time must be greater than start_time" in str(exc_info.value)

    def test_end_time_less_than_start_time(self):
        """Test end_time less than start_time raises error."""
        with pytest.raises(ValidationError):
            ClipRequest(
                url="https://www.youtube.com/watch?v=dQw4w9WgXcQ",
                start_time=100,
                end_time=50
            )

    def test_negative_start_time(self):
        """Test negative start_time raises error."""
        with pytest.raises(ValidationError):
            ClipRequest(
                url="https://www.youtube.com/watch?v=dQw4w9WgXcQ",
                start_time=-10,
                end_time=60
            )

    def test_negative_end_time(self):
        """Test negative end_time raises error."""
        with pytest.raises(ValidationError):
            ClipRequest(
                url="https://www.youtube.com/watch?v=dQw4w9WgXcQ",
                start_time=0,
                end_time=-60
            )


class TestVideoInfoResponseSchema:
    """Test video info response schemas."""

    def test_valid_video_info_response(self):
        """Test valid video info response."""
        response = VideoInfoResponse(
            video_id="dQw4w9WgXcQ",
            title="Test Video",
            duration=213,
            thumbnail="https://example.com/thumb.jpg",
            uploader="Test Uploader",
            description="Test description"
        )
        assert response.video_id == "dQw4w9WgXcQ"
        assert response.duration == 213


class TestClipResponseSchema:
    """Test clip response schemas."""

    def test_success_response(self):
        """Test successful clip response."""
        response = ClipResponse(
            success=True,
            message="Clip berhasil dibuat!",
            file_path="/api/download/abc123",
            file_size=5242880,
            session_id="abc123"
        )
        assert response.success is True
        assert response.file_size == 5242880

    def test_failure_response(self):
        """Test failure clip response."""
        response = ClipResponse(
            success=False,
            message="Video tidak ditemukan"
        )
        assert response.success is False
        assert response.file_path is None
        assert response.session_id is None


if __name__ == "__main__":
    pytest.main([__file__, "-v"])