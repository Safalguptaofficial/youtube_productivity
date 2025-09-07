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

### Start Backend
```bash
cd backend
python -m venv .venv
. .venv/bin/activate
pip install -r requirements.txt
uvicorn main:app --reload --port 8000
```

### Start Frontend
```bash
cd frontend
pnpm install
pnpm dev
```

## Quick Start

Use the Makefile for convenient development:

```bash
make dev-backend    # Start backend in development mode
make dev-frontend   # Start frontend in development mode
make dev            # Start both services
```
