#!/usr/bin/env python3
"""
Test script for YouTube Productivity Summarizer Module

This script tests the summarization and keyword extraction functionality.
"""

import os
import sys
from summarizer import (
    Summarizer, 
    summarize_text, 
    extract_keywords, 
    process_text,
    SummarizationError
)

# Sample text for testing
SAMPLE_TEXT = """
Artificial intelligence (AI) has revolutionized the way we approach problem-solving and automation in the modern world. 
From simple chatbots to complex machine learning algorithms, AI systems are now integrated into virtually every industry. 
The healthcare sector has particularly benefited from AI advancements, with diagnostic tools that can analyze medical images 
with unprecedented accuracy. In the financial industry, AI algorithms help detect fraudulent transactions and make 
investment decisions based on vast amounts of market data. Transportation has been transformed by autonomous vehicles 
and smart traffic management systems that reduce congestion and improve safety. However, the rapid advancement of AI 
also brings challenges, including concerns about job displacement, privacy issues, and the need for ethical guidelines 
in AI development. As we move forward, it's crucial to balance the benefits of AI with responsible implementation 
that considers the societal impact. The future of AI holds promise for solving some of humanity's most pressing 
problems, from climate change to disease prevention, but it requires careful planning and collaboration between 
technologists, policymakers, and society at large.
"""

def test_initialization():
    """Test summarizer initialization"""
    print("🧪 Testing Summarizer Initialization...")
    try:
        summarizer = Summarizer()
        print("✅ Summarizer initialized successfully")
        
        # Check which method is being used
        if summarizer.hf_inference:
            print("   🔗 Using Hugging Face Inference API")
        elif summarizer.summarizer:
            print("   🏠 Using local transformers pipeline")
        else:
            print("   ❌ No summarization method available")
            return False
            
        return True
    except SummarizationError as e:
        print(f"❌ Initialization failed: {e}")
        return False
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return False


def test_text_chunking():
    """Test text chunking functionality"""
    print("\n🧪 Testing Text Chunking...")
    try:
        summarizer = Summarizer()
        chunks = summarizer.chunk_text(SAMPLE_TEXT, max_tokens=200)
        
        print(f"✅ Text chunked into {len(chunks)} pieces")
        for i, chunk in enumerate(chunks):
            print(f"   Chunk {i+1}: {len(chunk)} characters")
            print(f"   Preview: {chunk[:100]}...")
        
        return len(chunks) > 0
    except Exception as e:
        print(f"❌ Chunking failed: {e}")
        return False


def test_keyword_extraction():
    """Test keyword extraction"""
    print("\n🧪 Testing Keyword Extraction...")
    try:
        keywords = extract_keywords(SAMPLE_TEXT, top_k=8)
        
        print(f"✅ Extracted {len(keywords)} keywords:")
        for i, keyword in enumerate(keywords, 1):
            print(f"   {i}. {keyword}")
        
        return len(keywords) > 0
    except Exception as e:
        print(f"❌ Keyword extraction failed: {e}")
        return False


def test_summarization():
    """Test text summarization"""
    print("\n🧪 Testing Text Summarization...")
    try:
        result = summarize_text(SAMPLE_TEXT)
        
        print("✅ Summarization completed successfully:")
        print(f"   📊 Number of chunks: {result['num_chunks']}")
        print(f"   📝 Total tokens (approx): {result['total_tokens']}")
        print(f"   📄 Short summary: {result['short_summary']}")
        print(f"   📖 Long summary: {result['long_summary']}")
        print(f"   📋 Chunk summaries: {len(result['chunk_summaries'])} chunks")
        
        # Show first chunk summary
        if result['chunk_summaries']:
            print(f"   Preview chunk summary: {result['chunk_summaries'][0][:100]}...")
        
        return True
    except SummarizationError as e:
        print(f"❌ Summarization failed: {e}")
        return False
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return False


def test_complete_pipeline():
    """Test complete text processing pipeline"""
    print("\n🧪 Testing Complete Processing Pipeline...")
    try:
        result = process_text(SAMPLE_TEXT, extract_keywords=True)
        
        print("✅ Complete pipeline executed successfully:")
        print(f"   📊 Number of chunks: {result.num_chunks}")
        print(f"   📝 Total tokens (approx): {result.total_tokens}")
        print(f"   📄 Short summary: {result.short_summary}")
        print(f"   📖 Long summary: {result.long_summary}")
        print(f"   🔑 Keywords: {', '.join(result.keywords)}")
        print(f"   📋 Chunk summaries: {len(result.chunk_summaries)} chunks")
        
        return True
    except SummarizationError as e:
        print(f"❌ Pipeline failed: {e}")
        return False
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return False


def test_environment_config():
    """Test environment configuration"""
    print("\n🧪 Testing Environment Configuration...")
    
    hf_api_key = os.getenv("HF_API_KEY")
    use_local = os.getenv("USE_LOCAL_MODELS", "false").lower() == "true"
    
    print(f"   🔑 HF_API_KEY: {'Set' if hf_api_key else 'Not set'}")
    print(f"   🏠 USE_LOCAL_MODELS: {use_local}")
    
    if hf_api_key and not use_local:
        print("   📡 Will use Hugging Face Inference API")
    elif use_local:
        print("   🏠 Will use local transformers")
    else:
        print("   ⚠️  Will fallback to local transformers (if available)")
    
    return True


def main():
    """Main test function"""
    print("🚀 YouTube Productivity Summarizer Test")
    print("=" * 50)
    print(f"📝 Sample text length: {len(SAMPLE_TEXT)} characters")
    print()
    
    # Test environment configuration
    test_environment_config()
    
    # Test individual functions
    init_success = test_initialization()
    chunk_success = test_text_chunking()
    keyword_success = test_keyword_extraction()
    summary_success = test_summarization()
    pipeline_success = test_complete_pipeline()
    
    # Summary
    print("\n📊 Test Summary:")
    print("=" * 30)
    print(f"✅ Initialization: {'PASS' if init_success else 'FAIL'}")
    print(f"✅ Text chunking: {'PASS' if chunk_success else 'FAIL'}")
    print(f"✅ Keyword extraction: {'PASS' if keyword_success else 'FAIL'}")
    print(f"✅ Summarization: {'PASS' if summary_success else 'FAIL'}")
    print(f"✅ Complete pipeline: {'PASS' if pipeline_success else 'FAIL'}")
    
    # Overall result
    all_passed = all([init_success, chunk_success, keyword_success, summary_success, pipeline_success])
    print(f"\n🎯 Overall Result: {'PASS' if all_passed else 'FAIL'}")
    
    if all_passed:
        print("\n🎉 All tests passed! Summarizer is ready for production.")
    else:
        print("\n⚠️  Some tests failed. Check the output above for details.")
    
    print("\n💡 Tips:")
    print("   - Set HF_API_KEY for faster inference via Hugging Face API")
    print("   - Set USE_LOCAL_MODELS=true to force local transformers")
    print("   - Install scikit-learn for better keyword extraction")


if __name__ == "__main__":
    main()
