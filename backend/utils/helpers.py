"""
Helper utility functions.
"""
from typing import Optional


def format_duration(seconds: int) -> str:
    """Format seconds to HH:MM:SS string."""
    hours = seconds // 3600
    minutes = (seconds % 3600) // 60
    secs = seconds % 60
    return f"{hours:02d}:{minutes:02d}:{secs:02d}"


def parse_duration(duration_str: str) -> Optional[int]:
    """
    Parse duration string to seconds.
    Supports formats: HH:MM:SS, MM:SS, SS
    """
    try:
        parts = duration_str.strip().split(':')
        parts = [int(p) for p in parts]
        
        if len(parts) == 3:
            hours, minutes, seconds = parts
            return hours * 3600 + minutes * 60 + seconds
        elif len(parts) == 2:
            minutes, seconds = parts
            return minutes * 60 + seconds
        elif len(parts) == 1:
            return parts[0]
        return None
    except (ValueError, AttributeError):
        return None


def format_file_size(bytes_size: int) -> str:
    """Format bytes to human readable string."""
    for unit in ['B', 'KB', 'MB', 'GB']:
        if bytes_size < 1024:
            return f"{bytes_size:.1f} {unit}"
        bytes_size /= 1024
    return f"{bytes_size:.1f} TB"


def sanitize_filename(filename: str) -> str:
    """Remove invalid characters from filename."""
    import re
    # Remove characters that are invalid in filenames
    filename = re.sub(r'[<>:"/\\|?*]', '', filename)
    # Replace spaces with underscores
    filename = filename.replace(' ', '_')
    # Limit length
    return filename[:100]