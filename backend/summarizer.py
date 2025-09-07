"""
YouTube Productivity Summarizer Module

This module provides text summarization and keyword extraction capabilities
using Hugging Face transformers and inference API.
"""

import os
import re
import logging
from typing import List, Dict, Optional, Union
from dataclasses import dataclass

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Try to import optional dependencies
try:
    from transformers import pipeline
    TRANSFORMERS_AVAILABLE = True
except ImportError:
    TRANSFORMERS_AVAILABLE = False
    logger.warning("transformers not available, will use HF Inference API only")

try:
    from huggingface_hub import InferenceApi
    HF_HUB_AVAILABLE = True
except ImportError:
    HF_HUB_AVAILABLE = False
    logger.warning("huggingface_hub not available, will use local transformers only")

try:
    from sklearn.feature_extraction.text import TfidfVectorizer
    from sklearn.metrics.pairwise import cosine_similarity
    import numpy as np
    SKLEARN_AVAILABLE = True
except ImportError:
    SKLEARN_AVAILABLE = False
    logger.warning("scikit-learn not available, will use basic keyword extraction")


@dataclass
class SummarizationResult:
    """Result of text summarization"""
    short_summary: str
    long_summary: str
    chunk_summaries: List[str]
    keywords: List[str]
    num_chunks: int
    total_tokens: int


class SummarizationError(Exception):
    """Custom exception for summarization errors"""
    pass


class Summarizer:
    """Main summarization class with HF API and local model support"""
    
    def __init__(self):
        self.hf_api_key = os.getenv("HF_API_KEY")
        self.use_local_models = os.getenv("USE_LOCAL_MODELS", "false").lower() == "true"
        self.model_name = "sshleifer/distilbart-cnn-12-6"
        
        # Initialize summarization pipeline
        self.summarizer = None
        self.hf_inference = None
        
        self._initialize_summarizer()
    
    def _initialize_summarizer(self):
        """Initialize the summarization pipeline"""
        try:
            if self.hf_api_key and not self.use_local_models and HF_HUB_AVAILABLE:
                # Use HF Inference API
                logger.info("Initializing Hugging Face Inference API")
                self.hf_inference = InferenceApi(
                    repo_id=self.model_name,
                    token=self.hf_api_key
                )
                logger.info("✅ HF Inference API initialized")
                
            elif TRANSFORMERS_AVAILABLE:
                # Use local transformers
                logger.info("Initializing local transformers pipeline")
                self.summarizer = pipeline(
                    "summarization",
                    model=self.model_name,
                    tokenizer=self.model_name,
                    device=-1  # Use CPU
                )
                logger.info("✅ Local transformers pipeline initialized")
                
            else:
                raise SummarizationError(
                    "No summarization method available. Install transformers or provide HF_API_KEY"
                )
                
        except Exception as e:
            logger.error(f"Error initializing summarizer: {e}")
            raise SummarizationError(f"Failed to initialize summarizer: {e}")
    
    def _summarize_text(self, text: str, max_length: int = 150, min_length: int = 30) -> str:
        """Summarize text using available method"""
        try:
            if self.hf_inference:
                # Use HF Inference API
                result = self.hf_inference({
                    "inputs": text,
                    "parameters": {
                        "max_length": max_length,
                        "min_length": min_length,
                        "do_sample": False
                    }
                })
                
                if isinstance(result, list) and len(result) > 0:
                    return result[0].get("summary_text", "")
                else:
                    raise SummarizationError("Invalid response from HF Inference API")
                    
            elif self.summarizer:
                # Use local transformers
                result = self.summarizer(
                    text,
                    max_length=max_length,
                    min_length=min_length,
                    do_sample=False
                )
                
                if isinstance(result, list) and len(result) > 0:
                    return result[0].get("summary_text", "")
                else:
                    raise SummarizationError("Invalid response from local summarizer")
                    
            else:
                raise SummarizationError("No summarization method available")
                
        except Exception as e:
            logger.error(f"Error summarizing text: {e}")
            raise SummarizationError(f"Summarization failed: {e}")
    
    def chunk_text(self, text: str, max_tokens: int = 1000) -> List[str]:
        """
        Split text into chunks of approximately max_tokens length
        
        Args:
            text: Input text to chunk
            max_tokens: Approximate maximum tokens per chunk (using char count as proxy)
            
        Returns:
            List of text chunks
        """
        try:
            # Approximate tokens as characters / 4 (rough estimate)
            max_chars = max_tokens * 4
            
            # Split by sentences first
            sentences = re.split(r'[.!?]+', text)
            sentences = [s.strip() for s in sentences if s.strip()]
            
            chunks = []
            current_chunk = ""
            
            for sentence in sentences:
                # If adding this sentence would exceed max_chars, start a new chunk
                if len(current_chunk) + len(sentence) > max_chars and current_chunk:
                    chunks.append(current_chunk.strip())
                    current_chunk = sentence
                else:
                    current_chunk += " " + sentence if current_chunk else sentence
            
            # Add the last chunk if it's not empty
            if current_chunk.strip():
                chunks.append(current_chunk.strip())
            
            logger.info(f"Split text into {len(chunks)} chunks")
            return chunks
            
        except Exception as e:
            logger.error(f"Error chunking text: {e}")
            raise SummarizationError(f"Text chunking failed: {e}")
    
    def summarize_long_text(self, text: str) -> Dict[str, Union[str, List[str], int]]:
        """
        Summarize long text using multi-pass approach
        
        Args:
            text: Input text to summarize
            
        Returns:
            Dictionary with short_summary, long_summary, chunk_summaries, num_chunks, total_tokens
        """
        try:
            if not text or not text.strip():
                raise SummarizationError("Input text is empty")
            
            # Step 1: Chunk the text
            chunks = self.chunk_text(text)
            
            if not chunks:
                raise SummarizationError("No chunks created from input text")
            
            logger.info(f"Processing {len(chunks)} chunks for summarization")
            
            # Step 2: Summarize each chunk
            chunk_summaries = []
            for i, chunk in enumerate(chunks):
                try:
                    logger.info(f"Summarizing chunk {i+1}/{len(chunks)}")
                    chunk_summary = self._summarize_text(chunk, max_length=150, min_length=30)
                    chunk_summaries.append(chunk_summary)
                except Exception as e:
                    logger.warning(f"Failed to summarize chunk {i+1}: {e}")
                    # Use first part of chunk as fallback
                    chunk_summaries.append(chunk[:200] + "...")
            
            # Step 3: Join chunk summaries to form long summary
            long_summary_text = " ".join(chunk_summaries)
            
            # Step 4: Create final long summary
            long_summary = self._summarize_text(long_summary_text, max_length=300, min_length=100)
            
            # Step 5: Create short summary from long summary
            short_summary = self._summarize_text(long_summary, max_length=60, min_length=20)
            
            result = {
                "short_summary": short_summary,
                "long_summary": long_summary,
                "chunk_summaries": chunk_summaries,
                "num_chunks": len(chunks),
                "total_tokens": len(text) // 4  # Rough estimate
            }
            
            logger.info("✅ Summarization completed successfully")
            return result
            
        except Exception as e:
            logger.error(f"Error in summarize_long_text: {e}")
            raise SummarizationError(f"Long text summarization failed: {e}")
    
    def extract_keywords(self, text: str, top_k: int = 8) -> List[str]:
        """
        Extract keywords from text using TF-IDF or frequency-based approach
        
        Args:
            text: Input text
            top_k: Number of top keywords to return
            
        Returns:
            List of keywords
        """
        try:
            if not text or not text.strip():
                return []
            
            # Clean and preprocess text
            text = re.sub(r'[^\w\s]', ' ', text.lower())
            words = text.split()
            
            # Remove common stop words
            stop_words = {
                'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with',
                'by', 'is', 'are', 'was', 'were', 'be', 'been', 'being', 'have', 'has', 'had',
                'do', 'does', 'did', 'will', 'would', 'could', 'should', 'may', 'might', 'must',
                'can', 'this', 'that', 'these', 'those', 'i', 'you', 'he', 'she', 'it', 'we', 'they',
                'me', 'him', 'her', 'us', 'them', 'my', 'your', 'his', 'her', 'its', 'our', 'their'
            }
            
            # Filter words
            filtered_words = [word for word in words if word not in stop_words and len(word) > 2]
            
            if SKLEARN_AVAILABLE and len(filtered_words) > 10:
                # Use TF-IDF approach
                return self._extract_keywords_tfidf(text, top_k)
            else:
                # Use frequency-based approach
                return self._extract_keywords_frequency(filtered_words, top_k)
                
        except Exception as e:
            logger.error(f"Error extracting keywords: {e}")
            return []
    
    def _extract_keywords_tfidf(self, text: str, top_k: int) -> List[str]:
        """Extract keywords using TF-IDF"""
        try:
            # Split into sentences for TF-IDF
            sentences = re.split(r'[.!?]+', text)
            sentences = [s.strip() for s in sentences if s.strip() and len(s) > 10]
            
            if len(sentences) < 2:
                return self._extract_keywords_frequency(text.split(), top_k)
            
            # Create TF-IDF vectorizer
            vectorizer = TfidfVectorizer(
                max_features=1000,
                stop_words='english',
                ngram_range=(1, 2),
                min_df=1,
                max_df=0.8
            )
            
            # Fit and transform
            tfidf_matrix = vectorizer.fit_transform(sentences)
            feature_names = vectorizer.get_feature_names_out()
            
            # Get mean TF-IDF scores
            mean_scores = np.mean(tfidf_matrix.toarray(), axis=0)
            
            # Get top keywords
            top_indices = np.argsort(mean_scores)[-top_k:][::-1]
            keywords = [feature_names[i] for i in top_indices if mean_scores[i] > 0]
            
            return keywords[:top_k]
            
        except Exception as e:
            logger.warning(f"TF-IDF keyword extraction failed: {e}")
            return self._extract_keywords_frequency(text.split(), top_k)
    
    def _extract_keywords_frequency(self, words: List[str], top_k: int) -> List[str]:
        """Extract keywords using frequency-based approach"""
        try:
            # Count word frequencies
            word_freq = {}
            for word in words:
                word_freq[word] = word_freq.get(word, 0) + 1
            
            # Sort by frequency
            sorted_words = sorted(word_freq.items(), key=lambda x: x[1], reverse=True)
            
            # Return top keywords
            keywords = [word for word, freq in sorted_words[:top_k] if freq > 1]
            
            return keywords
            
        except Exception as e:
            logger.error(f"Frequency-based keyword extraction failed: {e}")
            return []
    
    def process_text(self, text: str, extract_keywords: bool = True) -> SummarizationResult:
        """
        Complete text processing pipeline
        
        Args:
            text: Input text to process
            extract_keywords: Whether to extract keywords
            
        Returns:
            SummarizationResult object
        """
        try:
            # Summarize the text
            summary_result = self.summarize_long_text(text)
            
            # Extract keywords if requested
            keywords = []
            if extract_keywords:
                keywords = self.extract_keywords(text)
            
            return SummarizationResult(
                short_summary=summary_result["short_summary"],
                long_summary=summary_result["long_summary"],
                chunk_summaries=summary_result["chunk_summaries"],
                keywords=keywords,
                num_chunks=summary_result["num_chunks"],
                total_tokens=summary_result["total_tokens"]
            )
            
        except Exception as e:
            logger.error(f"Error in process_text: {e}")
            raise SummarizationError(f"Text processing failed: {e}")


# Global summarizer instance
_summarizer_instance = None

def get_summarizer() -> Summarizer:
    """Get or create global summarizer instance"""
    global _summarizer_instance
    if _summarizer_instance is None:
        _summarizer_instance = Summarizer()
    return _summarizer_instance


# Convenience functions
def summarize_text(text: str) -> Dict[str, Union[str, List[str], int]]:
    """Convenience function for text summarization"""
    summarizer = get_summarizer()
    return summarizer.summarize_long_text(text)


def extract_keywords(text: str, top_k: int = 8) -> List[str]:
    """Convenience function for keyword extraction"""
    summarizer = get_summarizer()
    return summarizer.extract_keywords(text, top_k)


def process_text(text: str, extract_keywords: bool = True) -> SummarizationResult:
    """Convenience function for complete text processing"""
    summarizer = get_summarizer()
    return summarizer.process_text(text, extract_keywords)
