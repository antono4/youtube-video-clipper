"""
Integration tests for API endpoints.
"""
import pytest
from fastapi.testclient import TestClient
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend.main import app
from backend.services.video_service import video_service


client = TestClient(app)


class TestRootEndpoint:
    """Test root endpoint."""

    def test_root_returns_app_info(self):
        """Test root endpoint returns app information."""
        response = client.get("/")
        assert response.status_code == 200
        data = response.json()
        assert "name" in data
        assert "version" in data
        assert "status" in data
        assert data["status"] == "running"

    def test_health_check(self):
        """Test health check endpoint."""
        response = client.get("/health")
        assert response.status_code == 200
        assert response.json() == {"status": "healthy"}


class TestValidateEndpoint:
    """Test /api/validate endpoint."""

    def test_validate_invalid_url(self):
        """Test validate endpoint with invalid URL."""
        response = client.post(
            "/api/validate",
            json={"url": "https://example.com/video"}
        )
        # Pydantic validation returns 422 for invalid URL format
        assert response.status_code == 422

    def test_validate_missing_url(self):
        """Test validate endpoint with missing URL."""
        response = client.post(
            "/api/validate",
            json={}
        )
        assert response.status_code == 422  # Validation error

    def test_validate_empty_url(self):
        """Test validate endpoint with empty URL."""
        response = client.post(
            "/api/validate",
            json={"url": ""}
        )
        assert response.status_code == 422


class TestProcessEndpoint:
    """Test /api/process endpoint."""

    def test_process_invalid_url(self):
        """Test process endpoint with invalid URL."""
        response = client.post(
            "/api/process",
            json={
                "url": "https://example.com/video",
                "start_time": 10,
                "end_time": 60
            }
        )
        # Should return success=False since validation happens
        assert response.status_code == 400 or response.status_code == 200

    def test_process_invalid_time_range(self):
        """Test process endpoint with end_time <= start_time."""
        # Pydantic validator catches end_time == start_time at schema level
        response = client.post(
            "/api/process",
            json={
                "url": "https://www.youtube.com/watch?v=dQw4w9WgXcQ",
                "start_time": 60,
                "end_time": 60
            }
        )
        assert response.status_code == 422  # Pydantic validation error

    def test_process_end_before_start(self):
        """Test process endpoint with end_time < start_time."""
        # This case should be caught by Pydantic validator
        response = client.post(
            "/api/process",
            json={
                "url": "https://www.youtube.com/watch?v=dQw4w9WgXcQ",
                "start_time": 100,
                "end_time": 50
            }
        )
        assert response.status_code == 422  # Pydantic validation error

    def test_process_negative_times(self):
        """Test process endpoint with negative times."""
        response = client.post(
            "/api/process",
            json={
                "url": "https://www.youtube.com/watch?v=dQw4w9WgXcQ",
                "start_time": -10,
                "end_time": 60
            }
        )
        assert response.status_code == 422  # Validation error

    def test_process_missing_fields(self):
        """Test process endpoint with missing fields."""
        response = client.post(
            "/api/process",
            json={"url": "https://www.youtube.com/watch?v=dQw4w9WgXcQ"}
        )
        assert response.status_code == 422


class TestDownloadEndpoint:
    """Test /api/download endpoint."""

    def test_download_nonexistent_file(self):
        """Test download endpoint with non-existent session."""
        response = client.get("/api/download/nonexistent-session-id")
        assert response.status_code == 404
        assert "tidak ditemukan" in response.json()["detail"]


class TestCleanupEndpoint:
    """Test /api/cleanup endpoint."""

    def test_cleanup_nonexistent_session(self):
        """Test cleanup endpoint with non-existent session."""
        response = client.delete("/api/cleanup/nonexistent-session-id")
        assert response.status_code == 200
        assert "cleaned up" in response.json()["message"].lower()


class TestVideoService:
    """Test video service functions."""

    def test_create_session(self):
        """Test session creation."""
        session_id = video_service.create_session()
        assert session_id is not None
        assert len(session_id) == 36  # UUID format
        # Cleanup
        video_service.cleanup_session(session_id)

    def test_cleanup_session(self):
        """Test session cleanup."""
        session_id = video_service.create_session()
        video_service.cleanup_session(session_id)
        # Verify session directory is removed
        session_dir = video_service.temp_dir / session_id
        assert not session_dir.exists()

    def test_get_video_info_invalid_url(self):
        """Test get_video_info with invalid URL."""
        from backend.core.exceptions import VideoProcessingError
        with pytest.raises(VideoProcessingError):
            video_service.get_video_info("https://example.com/video")


if __name__ == "__main__":
    pytest.main([__file__, "-v"])