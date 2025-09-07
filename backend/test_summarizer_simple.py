#!/usr/bin/env python3
"""
Simple test for summarizer module - tests basic functionality without heavy models
"""

import os
from summarizer import Summarizer, extract_keywords, SummarizationError

def test_basic_functionality():
    """Test basic functionality without heavy model loading"""
    print("🧪 Simple Summarizer Test")
    print("=" * 30)
    
    # Test text chunking
    sample_text = "This is a test sentence. This is another test sentence. And here is a third sentence for testing purposes."
    
    print("🔍 Testing text chunking:")
    try:
        summarizer = Summarizer()
        chunks = summarizer.chunk_text(sample_text, max_tokens=50)
        print(f"✅ Chunked into {len(chunks)} pieces")
        for i, chunk in enumerate(chunks):
            print(f"   Chunk {i+1}: {chunk}")
    except Exception as e:
        print(f"❌ Chunking failed: {e}")
    
    # Test keyword extraction
    print("\n🔑 Testing keyword extraction:")
    try:
        keywords = extract_keywords(sample_text, top_k=5)
        print(f"✅ Extracted keywords: {keywords}")
    except Exception as e:
        print(f"❌ Keyword extraction failed: {e}")
    
    # Test environment
    print("\n⚙️ Environment:")
    print(f"   HF_API_KEY: {'Set' if os.getenv('HF_API_KEY') else 'Not set'}")
    print(f"   USE_LOCAL_MODELS: {os.getenv('USE_LOCAL_MODELS', 'false')}")
    
    print("\n💡 To test full summarization:")
    print("   1. Set HF_API_KEY for faster inference")
    print("   2. Or wait for local model download (1.2GB)")
    print("   3. Run: python test_summarizer.py")

if __name__ == "__main__":
    test_basic_functionality()
