"""
Unit tests for the new feature endpoints.
"""
import pytest
from fastapi.testclient import TestClient
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend.main import app
from backend.api.schemas import (
    URLShortenRequest,
    URLShortenResponse,
    ThumbnailResponse,
    CloudUploadRequest,
    CloudUploadResponse,
    VideoMetadataResponse,
    ClipStatsResponse,
)


client = TestClient(app)


class TestURLShortenerSchema:
    """Test URL shortener schemas."""

    def test_valid_shorten_request(self):
        """Test valid URL shorten request."""
        request = URLShortenRequest(url="https://example.com/very/long/url")
        assert request.url == "https://example.com/very/long/url"

    def test_empty_url_rejected(self):
        """Test empty URL is rejected."""
        with pytest.raises(Exception):
            URLShortenRequest(url="")

    def test_shorten_response_success(self):
        """Test successful shorten response."""
        response = URLShortenResponse(
            success=True,
            original_url="https://example.com",
            short_url="https://shrtco.de/abc",
            short_url_2="https://shrtco.de/def",
            short_url_3="https://shrtco.de/ghi",
            share_url="https://shrtco.de/share/abc"
        )
        assert response.success is True
        assert response.short_url == "https://shrtco.de/abc"

    def test_shorten_response_failure(self):
        """Test failure shorten response."""
        response = URLShortenResponse(
            success=False,
            error="URL is not valid"
        )
        assert response.success is False
        assert response.error == "URL is not valid"


class TestThumbnailSchema:
    """Test thumbnail schemas."""

    def test_thumbnail_response_success(self):
        """Test successful thumbnail response."""
        response = ThumbnailResponse(
            success=True,
            video_id="dQw4w9WgXcQ",
            thumbnail_url="https://i.ytimg.com/vi/dQw4w9WgXcQ/maxresdefault.jpg",
            thumbnails={
                "maxresdefault": "https://i.ytimg.com/vi/dQw4w9WgXcQ/maxresdefault.jpg",
                "hqdefault": "https://i.ytimg.com/vi/dQw4w9WgXcQ/hqdefault.jpg",
            }
        )
        assert response.success is True
        assert response.video_id == "dQw4w9WgXcQ"

    def test_thumbnail_response_failure(self):
        """Test failure thumbnail response."""
        response = ThumbnailResponse(
            success=False,
            error="Video not found"
        )
        assert response.success is False


class TestCloudUploadSchema:
    """Test cloud upload schemas."""

    def test_valid_upload_request(self):
        """Test valid cloud upload request."""
        request = CloudUploadRequest(session_id="abc123-def456")
        assert request.session_id == "abc123-def456"

    def test_empty_session_id_rejected(self):
        """Test empty session_id is rejected."""
        with pytest.raises(Exception):
            CloudUploadRequest(session_id="")

    def test_upload_response_success(self):
        """Test successful upload response."""
        response = CloudUploadResponse(
            success=True,
            download_page="https://gofile.io/d/abc123",
            direct_link="https://store1.gofile.io/contents/download/abc123.mp4",
            file_name="clip_abc123-def456.mp4"
        )
        assert response.success is True
        assert response.download_page == "https://gofile.io/d/abc123"

    def test_upload_response_failure(self):
        """Test failure upload response."""
        response = CloudUploadResponse(
            success=False,
            error="File not found"
        )
        assert response.success is False


class TestVideoMetadataSchema:
    """Test video metadata schemas."""

    def test_metadata_response_success(self):
        """Test successful metadata response."""
        response = VideoMetadataResponse(
            success=True,
            author_name="Test Author",
            author_url="https://www.youtube.com/@testauthor",
            thumbnail_url="https://i.ytimg.com/vi/dQw4w9WgXcQ/maxresdefault.jpg",
            width=1920,
            height=1080
        )
        assert response.success is True
        assert response.author_name == "Test Author"

    def test_metadata_response_failure(self):
        """Test failure metadata response."""
        response = VideoMetadataResponse(
            success=False,
            error="Failed to fetch metadata"
        )
        assert response.success is False


class TestClipStatsSchema:
    """Test clip stats schemas."""

    def test_stats_response_success(self):
        """Test successful stats response."""
        response = ClipStatsResponse(
            success=True,
            session_id="abc123-def456",
            clip_duration=30,
            clip_size=5242880,
            created_at="2024-01-01T00:00:00",
            file_path="/tmp/youtube-clipper/abc123-def456/output.mp4"
        )
        assert response.success is True
        assert response.clip_size == 5242880


class TestNewFeatureEndpoints:
    """Test new feature API endpoints."""

    def test_thumbnail_endpoint(self):
        """Test thumbnail endpoint returns URLs."""
        response = client.get("/api/thumbnail/dQw4w9WgXcQ")
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert data["video_id"] == "dQw4w9WgXcQ"
        assert "thumbnails" in data
        assert "maxresdefault" in data["thumbnails"]

    def test_thumbnail_endpoint_with_quality(self):
        """Test thumbnail endpoint with quality parameter."""
        response = client.get("/api/thumbnail/dQw4w9WgXcQ?quality=hqdefault")
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert "hqdefault" in data["thumbnail_url"]

    def test_stats_nonexistent_session(self):
        """Test stats endpoint with non-existent session."""
        response = client.get("/api/stats/nonexistent-session-id")
        assert response.status_code == 404

    def test_shorten_endpoint_missing_url(self):
        """Test shorten endpoint with missing URL."""
        response = client.post(
            "/api/shorten",
            json={}
        )
        assert response.status_code == 422

    def test_upload_endpoint_missing_session_id(self):
        """Test upload endpoint with missing session_id."""
        response = client.post(
            "/api/upload",
            json={}
        )
        assert response.status_code == 422

    def test_metadata_endpoint(self):
        """Test metadata endpoint."""
        response = client.get("/api/metadata/dQw4w9WgXcQ")
        # May fail if YouTube API is not accessible, but should return valid structure
        assert response.status_code == 200
        data = response.json()
        assert "success" in data


if __name__ == "__main__":
    pytest.main([__file__, "-v"])