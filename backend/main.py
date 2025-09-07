"""
YouTube Productivity Backend API
FastAPI application for processing YouTube videos
"""

import os
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv

# Load environment variables
load_dotenv()


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


if __name__ == "__main__":
    import uvicorn
    
    port = int(os.getenv("BACKEND_PORT", 8000))
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=port,
        reload=True
    )
