"""
External API services for URL shortening, screenshots, and cloud uploads.
"""
import httpx
import logging
from typing import Optional, Dict, Any

logger = logging.getLogger(__name__)


class URLShortenerService:
    """Service for shortening URLs using Shrtco.de API."""
    
    API_URL = "https://api.shrtco.de/v2"
    
    @staticmethod
    async def shorten_url(url: str) -> Dict[str, Any]:
        """
        Shorten a URL using Shrtco.de API.
        
        Args:
            url: The URL to shorten
            
        Returns:
            Dict with shortened URLs and metadata
        """
        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.get(
                    f"{URLShortenerService.API_URL}/shorten",
                    params={"url": url}
                )
                
                if response.status_code == 201:
                    data = response.json()
                    return {
                        "success": True,
                        "original_url": url,
                        "short_url": data.get("result", {}).get("full_short_link"),
                        "short_url_2": data.get("result", {}).get("full_short_link2"),
                        "short_url_3": data.get("result", {}).get("full_short_link3"),
                        "share_url": data.get("result", {}).get("share_link"),
                    }
                else:
                    return {
                        "success": False,
                        "error": f"API returned status {response.status_code}"
                    }
                    
        except Exception as e:
            logger.error(f"URL shortening error: {e}")
            return {
                "success": False,
                "error": str(e)
            }


class ScreenshotService:
    """Service for generating screenshots using ScreenshotLayer API."""
    
    API_URL = "http://api.screenshotlayer.com/api/capture"
    
    @staticmethod
    async def generate_thumbnail(
        url: str,
        width: int = 640,
        height: int = 480,
        format: str = "PNG"
    ) -> Optional[str]:
        """
        Generate a thumbnail screenshot of a URL.
        Note: Requires API key from screenshotlayer.com
        
        Args:
            url: The URL to capture
            width: Image width
            height: Image height
            format: Image format (PNG, JPG, GIF)
            
        Returns:
            Base64 encoded image or None
        """
        # ScreenshotLayer requires API key - using placeholder
        # In production, this would use an actual API key
        logger.info(f"Screenshot requested for: {url}")
        
        # Return placeholder - would need API key in production
        return None
    
    @staticmethod
    def generate_youtube_thumbnail_url(video_id: str, quality: str = "maxresdefault") -> str:
        """
        Generate standard YouTube thumbnail URL.
        
        Args:
            video_id: YouTube video ID
            quality: Thumbnail quality (maxresdefault, hqdefault, mqdefault, sddefault)
            
        Returns:
            YouTube thumbnail URL
        """
        return f"https://i.ytimg.com/vi/{video_id}/{quality}.jpg"


class CloudUploadService:
    """Service for uploading files to cloud storage."""
    
    GOFILE_API = "https://api.gofile.io/servers"
    
    @staticmethod
    async def upload_to_gofile(file_path: str, filename: str) -> Dict[str, Any]:
        """
        Upload a file to GoFile.io cloud storage.
        
        Args:
            file_path: Path to the file
            filename: Name for the uploaded file
            
        Returns:
            Dict with download URL and metadata
        """
        try:
            # Get server URL
            async with httpx.AsyncClient(timeout=30.0) as client:
                server_response = await client.get(CloudUploadService.GOFILE_API)
                
                if server_response.status_code != 200:
                    return {
                        "success": False,
                        "error": "Failed to get upload server"
                    }
                
                server_data = server_response.json()
                if server_data.get("status") != "ok":
                    return {
                        "success": False,
                        "error": "GoFile API unavailable"
                    }
                
                servers = server_data.get("data", {}).get("servers", [])
                if not servers:
                    return {
                        "success": False,
                        "error": "No available servers"
                    }
                
                server = servers[0].get("name", "store1")
                upload_url = f"https://{server}.gofile.io/contents/uploadfile"
                
                # Upload file
                with open(file_path, "rb") as f:
                    files = {"file": (filename, f, "video/mp4")}
                    upload_response = await client.post(
                        upload_url,
                        files=files
                    )
                
                if upload_response.status_code == 200:
                    result = upload_response.json()
                    if result.get("status") == "ok":
                        return {
                            "success": True,
                            "download_page": result.get("data", {}).get("downloadPage"),
                            "direct_link": result.get("data", {}).get("directLink"),
                            "file_name": filename,
                        }
                
                return {
                    "success": False,
                    "error": "Upload failed"
                }
                
        except Exception as e:
            logger.error(f"Cloud upload error: {e}")
            return {
                "success": False,
                "error": str(e)
            }


class VideoMetadataService:
    """Service for getting additional video metadata."""
    
    @staticmethod
    async def get_youtube_metadata(video_id: str) -> Dict[str, Any]:
        """
        Get additional metadata for a YouTube video.
        
        Args:
            video_id: YouTube video ID
            
        Returns:
            Dict with additional metadata
        """
        # Using YouTube's oEmbed API for basic info
        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.get(
                    "https://www.youtube.com/oembed",
                    params={
                        "url": f"https://www.youtube.com/watch?v={video_id}",
                        "format": "json"
                    }
                )
                
                if response.status_code == 200:
                    data = response.json()
                    return {
                        "success": True,
                        "author_name": data.get("author_name"),
                        "author_url": data.get("author_url"),
                        "thumbnail_url": data.get("thumbnail_url"),
                        "html_embed": data.get("html"),
                        "width": data.get("width"),
                        "height": data.get("height"),
                    }
                else:
                    return {
                        "success": False,
                        "error": "Failed to fetch metadata"
                    }
                    
        except Exception as e:
            logger.error(f"Metadata fetch error: {e}")
            return {
                "success": False,
                "error": str(e)
            }


# Singleton instances
url_shortener_service = URLShortenerService()
screenshot_service = ScreenshotService()
cloud_upload_service = CloudUploadService()
video_metadata_service = VideoMetadataService()