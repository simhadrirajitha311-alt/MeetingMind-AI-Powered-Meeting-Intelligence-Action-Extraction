# MeetingMind

AI-powered meeting intelligence and action extraction platform.

## Overview

MeetingMind lets teams upload audio or video recordings, process them with an AI workflow, and surface the most important outcomes from each call:

- transcript extraction and speaker-aware segmentation
- executive summary and topic detection
- decision capture and action-item tracking
- semantic search across the transcript
- grounded Q&A with source references
- exportable notes for downstream follow-up

## Stack

- Python 3.11+
- FastAPI backend
- SQLAlchemy + SQLite for persistence
- React + TypeScript + Vite frontend

## Local setup

1. Create and activate a virtual environment.
2. Install Python dependencies:

	```bash
	python -m pip install -r backend/requirements.txt
	```

3. Install frontend dependencies:

	```bash
	cd frontend && npm install
	```

4. Start the backend:

	```bash
	cd ..
	uvicorn backend.app.main:app --host 0.0.0.0 --port 8000 --reload
	```

5. Start the frontend:

	```bash
	cd frontend
	npm run dev -- --host 0.0.0.0
	```

6. Open the frontend address shown by Vite (for example, http://localhost:5173) and upload a meeting file.

## Demo mode

The application is set up to work without external API credentials in demo mode. It can still generate transcripts, summaries, action items, decisions, and search results from local sample data.

## Project structure

- backend/app: FastAPI app, DB layer, AI services, and routes
- frontend/src: React app shell and UI pages

## Verification

The app was validated with:

- `npm run build` in the frontend
- live backend health checks against `http://localhost:8000/meetings`
- live frontend HTTP check against the Vite dev server