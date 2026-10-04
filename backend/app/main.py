from __future__ import annotations

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from backend.app.api.router import router
from backend.app.core.config import settings
from backend.app.db.database import init_db

app = FastAPI(
    title='MeetingMind',
    version='1.0.0',
    description='AI-powered meeting intelligence and action extraction platform.',
    docs_url='/docs',
    redoc_url='/redoc',
)

origins = [origin.strip() for origin in settings.cors_origins.split(',') if origin.strip()]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins or ['*'],
    allow_credentials=True,
    allow_methods=['*'],
    allow_headers=['*'],
)

app.include_router(router)

init_db()


@app.on_event('startup')
def startup_event():
    init_db()
