"""
YouTube Productivity Worker Module

This module contains functions for processing YouTube videos:
- Fetching metadata (title, duration, thumbnail)
- Downloading auto-generated subtitles (VTT)
- Converting VTT to clean text
"""

import os
import re
import subprocess
import tempfile
from pathlib import Path
from typing import Dict, Optional, Union
import yt_dlp
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class YouTubeProcessingError(Exception):
    """Custom exception for YouTube processing errors"""
    pass


def ensure_temp_dir(job_id: str) -> Path:
    """
    Ensure temporary directory exists for a job
    
    Args:
        job_id: Unique job identifier
        
    Returns:
        Path to the temporary directory
    """
    temp_dir = Path("/tmp/ytprod") / job_id
    temp_dir.mkdir(parents=True, exist_ok=True)
    return temp_dir


def fetch_metadata(youtube_url: str) -> Dict[str, Union[str, int]]:
    """
    Fetch YouTube video metadata using yt-dlp
    
    Args:
        youtube_url: YouTube video URL
        
    Returns:
        Dictionary containing youtube_id, title, duration, thumbnail
        
    Raises:
        YouTubeProcessingError: If metadata extraction fails
    """
    try:
        # Extract video ID from URL
        youtube_id = extract_video_id(youtube_url)
        if not youtube_id:
            raise YouTubeProcessingError(f"Could not extract video ID from URL: {youtube_url}")
        
        # Configure yt-dlp options for metadata only
        ydl_opts = {
            'quiet': True,
            'no_warnings': True,
            'extract_flat': False,
        }
        
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            # Extract info without downloading
            info = ydl.extract_info(youtube_url, download=False)
            
            if not info:
                raise YouTubeProcessingError(f"Could not extract info for URL: {youtube_url}")
            
            # Extract relevant metadata
            metadata = {
                'youtube_id': youtube_id,
                'title': info.get('title', 'Unknown Title'),
                'duration': info.get('duration', 0),
                'thumbnail': info.get('thumbnail', ''),
                'uploader': info.get('uploader', 'Unknown'),
                'upload_date': info.get('upload_date', ''),
                'view_count': info.get('view_count', 0),
                'description': info.get('description', '')[:500] + '...' if info.get('description') else ''
            }
            
            logger.info(f"Successfully fetched metadata for video: {metadata['title']}")
            return metadata
            
    except Exception as e:
        logger.error(f"Error fetching metadata for {youtube_url}: {str(e)}")
        raise YouTubeProcessingError(f"Failed to fetch metadata: {str(e)}")


def get_transcript_vtt(youtube_url: str, out_dir: Union[str, Path], job_id: str) -> Optional[str]:
    """
    Download auto-generated subtitles (VTT) or fallback to audio for ASR
    
    Args:
        youtube_url: YouTube video URL
        out_dir: Output directory for files
        job_id: Unique job identifier
        
    Returns:
        Path to VTT file if found, None if not available
        
    Raises:
        YouTubeProcessingError: If download fails
    """
    try:
        out_dir = Path(out_dir)
        out_dir.mkdir(parents=True, exist_ok=True)
        
        # Configure yt-dlp options for subtitle download
        ydl_opts = {
            'writesubtitles': True,
            'writeautomaticsub': True,
            'subtitleslangs': ['en'],
            'skip_download': True,
            'outtmpl': str(out_dir / '%(title)s.%(ext)s'),
            'quiet': True,
            'no_warnings': True,
        }
        
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            # Try to download subtitles
            ydl.download([youtube_url])
            
            # Look for VTT files in the output directory
            vtt_files = list(out_dir.glob("*.vtt"))
            
            if vtt_files:
                vtt_path = vtt_files[0]  # Take the first VTT file found
                logger.info(f"Found VTT subtitle file: {vtt_path}")
                return str(vtt_path)
            else:
                # Fallback: download audio for ASR
                logger.info("No VTT subtitles found, downloading audio for ASR")
                return download_audio_for_asr(youtube_url, out_dir, job_id)
                
    except Exception as e:
        logger.error(f"Error downloading subtitles for {youtube_url}: {str(e)}")
        raise YouTubeProcessingError(f"Failed to download subtitles: {str(e)}")


def download_audio_for_asr(youtube_url: str, out_dir: Union[str, Path], job_id: str) -> Optional[str]:
    """
    Download audio file for ASR processing
    
    Args:
        youtube_url: YouTube video URL
        out_dir: Output directory for files
        job_id: Unique job identifier
        
    Returns:
        Path to audio file
        
    Raises:
        YouTubeProcessingError: If audio download fails
    """
    try:
        out_dir = Path(out_dir)
        
        # Configure yt-dlp options for audio extraction
        ydl_opts = {
            'format': 'bestaudio/best',
            'extractaudio': True,
            'audioformat': 'mp3',
            'outtmpl': str(out_dir / f'{job_id}_audio.%(ext)s'),
            'quiet': True,
            'no_warnings': True,
        }
        
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([youtube_url])
            
            # Look for audio files
            audio_files = list(out_dir.glob(f"{job_id}_audio.*"))
            
            if audio_files:
                audio_path = audio_files[0]
                logger.info(f"Downloaded audio file for ASR: {audio_path}")
                return str(audio_path)
            else:
                raise YouTubeProcessingError("Audio file not found after download")
                
    except Exception as e:
        logger.error(f"Error downloading audio for {youtube_url}: {str(e)}")
        raise YouTubeProcessingError(f"Failed to download audio: {str(e)}")


def vtt_to_text(vtt_path: Union[str, Path]) -> str:
    """
    Convert VTT subtitle file to clean plain text
    
    Args:
        vtt_path: Path to VTT file
        
    Returns:
        Clean plain text without timestamps
        
    Raises:
        YouTubeProcessingError: If VTT parsing fails
    """
    try:
        vtt_path = Path(vtt_path)
        
        if not vtt_path.exists():
            raise YouTubeProcessingError(f"VTT file not found: {vtt_path}")
        
        with open(vtt_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Remove VTT header
        content = re.sub(r'^WEBVTT\s*\n', '', content, flags=re.MULTILINE)
        
        # Remove timestamp lines (e.g., "00:00:01.000 --> 00:00:03.000")
        content = re.sub(r'\d{2}:\d{2}:\d{2}\.\d{3}\s*-->\s*\d{2}:\d{2}:\d{2}\.\d{3}', '', content)
        
        # Remove cue numbers (e.g., "1", "2", etc.)
        content = re.sub(r'^\d+\s*$', '', content, flags=re.MULTILINE)
        
        # Remove HTML tags
        content = re.sub(r'<[^>]+>', '', content)
        
        # Remove extra whitespace and normalize
        content = re.sub(r'\n\s*\n', '\n', content)
        content = re.sub(r'^\s+|\s+$', '', content, flags=re.MULTILINE)
        
        # Remove empty lines
        lines = [line.strip() for line in content.split('\n') if line.strip()]
        
        # Join lines with spaces
        clean_text = ' '.join(lines)
        
        logger.info(f"Converted VTT to text: {len(clean_text)} characters")
        return clean_text
        
    except Exception as e:
        logger.error(f"Error converting VTT to text: {str(e)}")
        raise YouTubeProcessingError(f"Failed to convert VTT to text: {str(e)}")


def extract_video_id(youtube_url: str) -> Optional[str]:
    """
    Extract YouTube video ID from URL
    
    Args:
        youtube_url: YouTube video URL
        
    Returns:
        Video ID or None if not found
    """
    patterns = [
        r'(?:youtube\.com/watch\?v=|youtu\.be/|youtube\.com/embed/)([a-zA-Z0-9_-]{11})',
        r'youtube\.com/v/([a-zA-Z0-9_-]{11})',
    ]
    
    for pattern in patterns:
        match = re.search(pattern, youtube_url)
        if match:
            return match.group(1)
    
    return None


def cleanup_temp_files(job_id: str) -> None:
    """
    Clean up temporary files for a job
    
    Args:
        job_id: Unique job identifier
    """
    try:
        temp_dir = Path("/tmp/ytprod") / job_id
        if temp_dir.exists():
            import shutil
            shutil.rmtree(temp_dir)
            logger.info(f"Cleaned up temporary files for job: {job_id}")
    except Exception as e:
        logger.error(f"Error cleaning up temp files for job {job_id}: {str(e)}")


# Example usage and testing functions
def process_youtube_video(youtube_url: str, job_id: str) -> Dict[str, Union[str, int, None]]:
    """
    Complete YouTube video processing pipeline
    
    Args:
        youtube_url: YouTube video URL
        job_id: Unique job identifier
        
    Returns:
        Dictionary with metadata and transcript path
    """
    try:
        # Ensure temp directory
        temp_dir = ensure_temp_dir(job_id)
        
        # Fetch metadata
        metadata = fetch_metadata(youtube_url)
        
        # Try to get transcript
        transcript_path = get_transcript_vtt(youtube_url, temp_dir, job_id)
        
        # Convert VTT to text if available
        transcript_text = None
        if transcript_path and transcript_path.endswith('.vtt'):
            transcript_text = vtt_to_text(transcript_path)
        
        result = {
            **metadata,
            'transcript_path': transcript_path,
            'transcript_text': transcript_text,
            'job_id': job_id
        }
        
        logger.info(f"Successfully processed video: {metadata['title']}")
        return result
        
    except Exception as e:
        logger.error(f"Error processing video {youtube_url}: {str(e)}")
        raise YouTubeProcessingError(f"Video processing failed: {str(e)}")
