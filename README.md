# YouTube Productivity Project

A monorepo for building productivity tools around YouTube content management and analysis.

## Project Structure

- `frontend/` - React/Next.js frontend application
- `backend/` - FastAPI Python backend service
- `supabase/` - Database schema and migrations

## Development Prerequisites

- Node.js 18+ 
- Python 3.10+
- yt-dlp installed globally (`pip install yt-dlp`)

## Development Setup

### Backend (FastAPI)

1. **Setup Python environment:**
```bash
cd backend
python -m venv .venv
. .venv/bin/activate  # On Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

2. **Configure environment:**
```bash
cp .env.example .env
# Edit .env with your Supabase credentials
```

3. **Run the backend:**
```bash
uvicorn main:app --reload --port 8000
```

4. **Test the API:**
```bash
curl http://localhost:8000/health
# Expected: {"status":"ok"}
```

### Frontend (React/Next.js)
```bash
cd frontend
pnpm install
pnpm dev
```

## Docker Setup

### Build Backend Docker Image
```bash
cd backend
docker build -t yt-prod-backend .
```

### Run Backend Container
```bash
docker run -p 8000:8000 --env-file .env yt-prod-backend
```

## Quick Start

Use the Makefile for convenient development:

```bash
make dev-backend    # Start backend in development mode
make dev-frontend   # Start frontend in development mode
make dev            # Start both services
```
