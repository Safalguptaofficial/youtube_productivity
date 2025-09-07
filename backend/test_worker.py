#!/usr/bin/env python3
"""
Test script for YouTube Productivity Worker Module

This script tests the worker functions with a real YouTube video.
"""

import os
import sys
import tempfile
from pathlib import Path
from worker import (
    fetch_metadata, 
    get_transcript_vtt, 
    vtt_to_text, 
    process_youtube_video,
    cleanup_temp_files,
    YouTubeProcessingError
)

# Test YouTube URL - replace with a public YouTube video for testing
YOUTUBE_TEST_URL = "https://www.youtube.com/watch?v=dQw4w9WgXcQ"  # Rick Roll - short, has subtitles

def test_fetch_metadata():
    """Test metadata fetching"""
    print("🧪 Testing fetch_metadata...")
    try:
        metadata = fetch_metadata(YOUTUBE_TEST_URL)
        print("✅ Metadata fetched successfully:")
        print(f"   📺 Title: {metadata['title']}")
        print(f"   🆔 YouTube ID: {metadata['youtube_id']}")
        print(f"   ⏱️  Duration: {metadata['duration']} seconds")
        print(f"   🖼️  Thumbnail: {metadata['thumbnail'][:50]}...")
        print(f"   👤 Uploader: {metadata['uploader']}")
        print(f"   👀 Views: {metadata['view_count']:,}")
        return metadata
    except YouTubeProcessingError as e:
        print(f"❌ Error fetching metadata: {e}")
        return None
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return None


def test_transcript_download():
    """Test transcript download"""
    print("\n🧪 Testing transcript download...")
    try:
        # Create temporary directory
        temp_dir = Path(tempfile.mkdtemp(prefix="yt_test_"))
        job_id = "test_job_123"
        
        transcript_path = get_transcript_vtt(YOUTUBE_TEST_URL, temp_dir, job_id)
        
        if transcript_path:
            print(f"✅ Transcript downloaded: {transcript_path}")
            
            # Check if it's a VTT file
            if transcript_path.endswith('.vtt'):
                print("📝 VTT file found, testing conversion to text...")
                try:
                    text = vtt_to_text(transcript_path)
                    print(f"✅ VTT converted to text: {len(text)} characters")
                    print(f"   Preview: {text[:200]}...")
                    return transcript_path, text
                except Exception as e:
                    print(f"❌ Error converting VTT: {e}")
                    return transcript_path, None
            else:
                print(f"🎵 Audio file downloaded for ASR: {transcript_path}")
                return transcript_path, None
        else:
            print("❌ No transcript or audio file downloaded")
            return None, None
            
    except YouTubeProcessingError as e:
        print(f"❌ Error downloading transcript: {e}")
        return None, None
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return None, None


def test_complete_pipeline():
    """Test complete video processing pipeline"""
    print("\n🧪 Testing complete processing pipeline...")
    try:
        job_id = "test_pipeline_456"
        result = process_youtube_video(YOUTUBE_TEST_URL, job_id)
        
        print("✅ Complete pipeline executed successfully:")
        print(f"   📺 Title: {result['title']}")
        print(f"   🆔 YouTube ID: {result['youtube_id']}")
        print(f"   ⏱️  Duration: {result['duration']} seconds")
        print(f"   📝 Transcript Path: {result['transcript_path']}")
        print(f"   📄 Transcript Text Length: {len(result['transcript_text']) if result['transcript_text'] else 0} characters")
        
        if result['transcript_text']:
            print(f"   Preview: {result['transcript_text'][:200]}...")
        
        return result
        
    except YouTubeProcessingError as e:
        print(f"❌ Error in pipeline: {e}")
        return None
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return None


def main():
    """Main test function"""
    print("🚀 YouTube Productivity Worker Test")
    print("=" * 50)
    print(f"🎯 Test URL: {YOUTUBE_TEST_URL}")
    print()
    
    # Test individual functions
    metadata = test_fetch_metadata()
    transcript_path, transcript_text = test_transcript_download()
    
    # Test complete pipeline
    pipeline_result = test_complete_pipeline()
    
    # Summary
    print("\n📊 Test Summary:")
    print("=" * 30)
    print(f"✅ Metadata fetch: {'PASS' if metadata else 'FAIL'}")
    print(f"✅ Transcript download: {'PASS' if transcript_path else 'FAIL'}")
    print(f"✅ VTT to text: {'PASS' if transcript_text else 'FAIL'}")
    print(f"✅ Complete pipeline: {'PASS' if pipeline_result else 'FAIL'}")
    
    # Cleanup
    print("\n🧹 Cleaning up test files...")
    try:
        cleanup_temp_files("test_job_123")
        cleanup_temp_files("test_pipeline_456")
        print("✅ Cleanup completed")
    except Exception as e:
        print(f"⚠️  Cleanup warning: {e}")
    
    print("\n🎉 Test completed!")


if __name__ == "__main__":
    main()
