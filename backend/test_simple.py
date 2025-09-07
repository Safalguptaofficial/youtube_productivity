#!/usr/bin/env python3
"""
Simple test for worker module - tests metadata only to avoid rate limits
"""

from worker import fetch_metadata, extract_video_id, YouTubeProcessingError

def test_simple():
    """Simple test focusing on metadata extraction"""
    print("🧪 Simple Worker Test")
    print("=" * 30)
    
    # Test video ID extraction
    test_urls = [
        "https://www.youtube.com/watch?v=dQw4w9WgXcQ",
        "https://youtu.be/dQw4w9WgXcQ",
        "https://www.youtube.com/embed/dQw4w9WgXcQ"
    ]
    
    print("🔍 Testing video ID extraction:")
    for url in test_urls:
        video_id = extract_video_id(url)
        print(f"   {url} -> {video_id}")
    
    print("\n📺 Testing metadata fetch:")
    try:
        metadata = fetch_metadata("https://www.youtube.com/watch?v=dQw4w9WgXcQ")
        print("✅ Metadata fetch successful!")
        print(f"   Title: {metadata['title']}")
        print(f"   Duration: {metadata['duration']} seconds")
        print(f"   Uploader: {metadata['uploader']}")
        print(f"   Views: {metadata['view_count']:,}")
        return True
    except YouTubeProcessingError as e:
        print(f"❌ Error: {e}")
        return False

if __name__ == "__main__":
    test_simple()
