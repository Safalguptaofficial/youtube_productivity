"""
YouTube Productivity Backend API
FastAPI application for processing YouTube videos
"""

import os
import uuid
from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, HttpUrl
from dotenv import load_dotenv
from worker import fetch_metadata, get_transcript_vtt, vtt_to_text, process_youtube_video, YouTubeProcessingError

# Load environment variables
load_dotenv()


# Pydantic models
class VideoMetadataRequest(BaseModel):
    youtube_url: HttpUrl


class VideoMetadataResponse(BaseModel):
    youtube_id: str
    title: str
    duration: int
    thumbnail: str
    uploader: str
    upload_date: str
    view_count: int
    description: str


class VideoProcessingRequest(BaseModel):
    youtube_url: HttpUrl


class VideoProcessingResponse(BaseModel):
    job_id: str
    youtube_id: str
    title: str
    duration: int
    thumbnail: str
    uploader: str
    upload_date: str
    view_count: int
    description: str
    transcript_path: str = None
    transcript_text: str = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan events"""
    # Startup
    print("🚀 Starting YouTube Productivity Backend...")
    print(f"📍 Environment: {os.getenv('NODE_ENV', 'development')}")
    print(f"🔗 Supabase URL: {os.getenv('SUPABASE_URL', 'Not configured')}")
    yield
    # Shutdown
    print("👋 Shutting down YouTube Productivity Backend...")


# Create FastAPI app
app = FastAPI(
    title="YouTube Productivity API",
    description="Backend API for YouTube video processing and analysis",
    version="1.0.0",
    lifespan=lifespan
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure this properly for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "YouTube Productivity API",
        "version": "1.0.0",
        "status": "running"
    }


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "ok"}


@app.get("/info")
async def app_info():
    """Application information endpoint"""
    return {
        "app": "YouTube Productivity Backend",
        "version": "1.0.0",
        "environment": os.getenv("NODE_ENV", "development"),
        "supabase_configured": bool(os.getenv("SUPABASE_URL")),
        "features": [
            "YouTube video processing",
            "Transcript extraction",
            "AI-powered summarization",
            "Keyword extraction"
        ]
    }


@app.post("/api/v1/metadata", response_model=VideoMetadataResponse)
async def get_video_metadata(request: VideoMetadataRequest):
    """Get YouTube video metadata"""
    try:
        metadata = fetch_metadata(str(request.youtube_url))
        return VideoMetadataResponse(**metadata)
    except YouTubeProcessingError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@app.post("/api/v1/process", response_model=VideoProcessingResponse)
async def process_video(request: VideoProcessingRequest):
    """Process YouTube video (metadata + transcript)"""
    try:
        job_id = str(uuid.uuid4())
        result = process_youtube_video(str(request.youtube_url), job_id)
        return VideoProcessingResponse(**result)
    except YouTubeProcessingError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@app.get("/api/v1/test")
async def test_worker():
    """Test endpoint for worker functionality"""
    try:
        # Test with a simple video
        test_url = "https://www.youtube.com/watch?v=dQw4w9WgXcQ"
        metadata = fetch_metadata(test_url)
        return {
            "status": "success",
            "message": "Worker module is functioning correctly",
            "test_metadata": {
                "title": metadata["title"],
                "duration": metadata["duration"],
                "uploader": metadata["uploader"]
            }
        }
    except Exception as e:
        return {
            "status": "error",
            "message": f"Worker test failed: {str(e)}"
        }


if __name__ == "__main__":
    import uvicorn
    
    port = int(os.getenv("BACKEND_PORT", 8000))
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=port,
        reload=True
    )
