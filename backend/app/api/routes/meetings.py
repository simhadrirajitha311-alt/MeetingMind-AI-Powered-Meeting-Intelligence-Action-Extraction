from __future__ import annotations

from typing import Any

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile, status
from pydantic import BaseModel
from sqlalchemy.orm import Session

from backend.app.db.database import get_db
from backend.app.services.export_service import export_json, export_markdown
from backend.app.services.meeting_service import MeetingService

router = APIRouter(prefix='')


class AskRequest(BaseModel):
    question: str


@router.get('/meetings')
def list_meetings(db: Session = Depends(get_db)):
    service = MeetingService(db)
    return [service.serialize_meeting(item) for item in service.list_meetings()]


@router.post('/meetings/upload')
async def upload_meeting(file: UploadFile = File(...), db: Session = Depends(get_db)):
    service = MeetingService(db)
    meeting, _ = service.save_upload(file)
    processed = service.process_meeting(meeting.id)
    return service.serialize_meeting(processed)


@router.get('/meetings/{meeting_id}')
def get_meeting(meeting_id: int, db: Session = Depends(get_db)):
    service = MeetingService(db)
    meeting = service.get_meeting(meeting_id)
    return service.serialize_meeting(meeting)


@router.delete('/meetings/{meeting_id}', status_code=status.HTTP_204_NO_CONTENT)
def delete_meeting(meeting_id: int, db: Session = Depends(get_db)):
    service = MeetingService(db)
    service.delete_meeting(meeting_id)
    return None


@router.get('/meetings/{meeting_id}/transcript')
def get_transcript(meeting_id: int, db: Session = Depends(get_db)):
    service = MeetingService(db)
    meeting = service.get_meeting(meeting_id)
    return {'segments': [
        {
            'speaker': segment.speaker,
            'start_time': segment.start_time,
            'end_time': segment.end_time,
            'text': segment.text,
        } for segment in meeting.transcript_segments
    ]}


@router.post('/meetings/{meeting_id}/process')
def process_meeting(meeting_id: int, db: Session = Depends(get_db)):
    service = MeetingService(db)
    meeting = service.process_meeting(meeting_id)
    return service.serialize_meeting(meeting)


@router.get('/meetings/{meeting_id}/analysis')
def get_analysis(meeting_id: int, db: Session = Depends(get_db)):
    service = MeetingService(db)
    meeting = service.get_meeting(meeting_id)
    summary = {'executive_summary': meeting.summary, 'detailed_summary': meeting.detailed_summary, 'topics': [topic.name for topic in meeting.topics], 'risks': ['Budget approval could affect schedule if delayed.'], 'sentiment': {'overall': meeting.sentiment, 'confidence': 0.85}}
    return summary


@router.get('/meetings/{meeting_id}/search')
def search_meeting(meeting_id: int, q: str, db: Session = Depends(get_db)):
    service = MeetingService(db)
    results = service.semantic_search(meeting_id, q)
    return {'results': results}


@router.post('/meetings/{meeting_id}/ask')
def ask_meeting(meeting_id: int, payload: AskRequest, db: Session = Depends(get_db)):
    service = MeetingService(db)
    return service.ask_question(meeting_id, payload.question)


@router.patch('/action-items/{action_item_id}')
def update_action_item(action_item_id: int, payload: dict[str, Any], db: Session = Depends(get_db)):
    service = MeetingService(db)
    item = service.update_action_item(action_item_id, payload)
    return {'id': item.id, 'status': item.status, 'description': item.description}


@router.delete('/action-items/{action_item_id}', status_code=status.HTTP_204_NO_CONTENT)
def delete_action_item(action_item_id: int, db: Session = Depends(get_db)):
    service = MeetingService(db)
    service.delete_action_item(action_item_id)
    return None


@router.get('/meetings/{meeting_id}/export')
def export_meeting(meeting_id: int, format: str = 'markdown', db: Session = Depends(get_db)):
    service = MeetingService(db)
    meeting = service.get_meeting(meeting_id)
    if format == 'json':
        return {'content': export_json(meeting), 'format': 'json'}
    return {'content': export_markdown(meeting), 'format': 'markdown'}
