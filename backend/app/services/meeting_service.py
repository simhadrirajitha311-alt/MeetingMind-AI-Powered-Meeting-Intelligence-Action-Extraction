from __future__ import annotations

import json
import os
import uuid
from datetime import datetime
from pathlib import Path

from fastapi import HTTPException, UploadFile
from sqlalchemy.orm import Session

from backend.app.ai.embeddings import EmbeddingService
from backend.app.ai.llm_provider import DemoLLMProvider, LLMProvider
from backend.app.ai.transcription import transcribe_audio_file
from backend.app.core.config import settings
from backend.app.db.models import ActionItem, Decision, Meeting, Question, Topic, TranscriptSegment
from backend.app.utils.chunking import chunk_transcript
from backend.app.utils.validation import validate_upload


class MeetingService:
    def __init__(self, db: Session):
        self.db = db
        self.embedding_service = EmbeddingService()
        self.llm_provider = DemoLLMProvider()

    def list_meetings(self):
        return self.db.query(Meeting).order_by(Meeting.created_at.desc()).all()

    def get_meeting(self, meeting_id: int):
        meeting = self.db.query(Meeting).filter(Meeting.id == meeting_id).first()
        if not meeting:
            raise HTTPException(status_code=404, detail='Meeting not found.')
        return meeting

    def create_meeting_record(self, filename: str, file_type: str, title: str | None = None):
        item = Meeting(
            title=title or filename,
            original_filename=filename,
            file_type=file_type,
            duration=0.0,
            status='uploaded',
            transcript='',
            summary='',
            detailed_summary='',
            sentiment='neutral',
        )
        self.db.add(item)
        self.db.commit()
        self.db.refresh(item)
        return item

    def save_upload(self, uploaded_file: UploadFile) -> tuple[Meeting, str]:
        extension = validate_upload(uploaded_file, settings.max_upload_size_mb)
        safe_name = f'{uuid.uuid4().hex}{extension}'
        storage_dir = Path(__file__).resolve().parents[2] / 'data' / 'uploads'
        storage_dir.mkdir(parents=True, exist_ok=True)
        destination = storage_dir / safe_name
        contents = uploaded_file.file.read()
        with open(destination, 'wb') as handle:
            handle.write(contents)

        title = uploaded_file.filename.rsplit('.', 1)[0].replace('_', ' ').strip() or 'Uploaded Meeting'
        meeting = self.create_meeting_record(uploaded_file.filename, extension.lstrip('.'), title)
        return meeting, str(destination)

    def process_meeting(self, meeting_id: int):
        meeting = self.get_meeting(meeting_id)
        meeting.status = 'processing'
        self.db.commit()

        file_path = Path(__file__).resolve().parents[2] / 'data' / 'uploads'
        candidates = sorted(file_path.glob(f'{meeting_id}*'))
        if len(candidates) == 0:
            candidates = sorted(file_path.glob(f'*{meeting.original_filename}'))
        source_file = str(candidates[0]) if candidates else None

        if source_file:
            transcription = transcribe_audio_file(source_file)
        else:
            transcription = {'segments': [
                {'speaker': 'Speaker 1', 'start_time': 0.0, 'end_time': 12.0, 'text': 'We agreed to launch the project next Friday and keep the workstream aligned.'},
                {'speaker': 'Speaker 2', 'start_time': 12.0, 'end_time': 24.0, 'text': 'I will finalize the marketing checklist and share it by Thursday.'},
            ], 'mode': 'demo'}

        segments = transcription.get('segments', [])
        for segment in segments:
            item = TranscriptSegment(
                meeting_id=meeting.id,
                speaker=segment.get('speaker', 'Speaker 1'),
                start_time=float(segment.get('start_time', 0.0)),
                end_time=float(segment.get('end_time', segment.get('start_time', 0.0))),
                text=segment.get('text', ''),
            )
            self.db.add(item)
        meeting.transcript = ' '.join(segment.get('text', '') for segment in segments)
        meeting.status = 'transcribing'
        self.db.commit()

        chunks = chunk_transcript(segments, max_chars=220, overlap=40)
        self.embedding_service.save_index(meeting.id, chunks)

        analysis = self.llm_provider.generate_analysis(meeting.transcript)
        if 'executive_summary' in analysis:
            meeting.summary = analysis.get('executive_summary', '')
            meeting.detailed_summary = analysis.get('detailed_summary', '')
            meeting.sentiment = analysis.get('sentiment', {}).get('overall', 'neutral')

        for decision in analysis.get('decisions', []):
            self.db.add(Decision(
                meeting_id=meeting.id,
                decision=decision.get('decision', ''),
                context=decision.get('context', ''),
                source_time=float(decision.get('source_timestamp', 0.0)),
            ))

        for item in analysis.get('action_items', []):
            self.db.add(ActionItem(
                meeting_id=meeting.id,
                description=item.get('task', ''),
                assignee=item.get('assignee', 'Unassigned'),
                deadline=item.get('deadline', 'Not specified'),
                priority=item.get('priority', 'medium'),
                status='open',
            ))

        for topic in analysis.get('topics', []):
            self.db.add(Topic(meeting_id=meeting.id, name=topic, description='Identified in transcript analysis.'))

        for question in analysis.get('questions', []):
            self.db.add(Question(
                meeting_id=meeting.id,
                question=question.get('question', ''),
                answer=question.get('answer', ''),
            ))

        meeting.status = 'completed'
        self.db.commit()
        self.db.refresh(meeting)
        return meeting

    def semantic_search(self, meeting_id: int, query: str):
        return self.embedding_service.similarity_search(meeting_id, query, top_k=5)

    def ask_question(self, meeting_id: int, question: str):
        meeting = self.get_meeting(meeting_id)
        context_entries = self.semantic_search(meeting_id, question)
        context = '\n'.join(f"{entry['speaker']} ({entry['start_time']}s): {entry['text']}" for entry in context_entries)
        response = self.llm_provider.answer_question(question, context)
        sources = response.get('sources', [])
        return {'answer': response.get('answer', ''), 'sources': sources}

    def update_action_item(self, action_item_id: int, payload: dict):
        action = self.db.query(ActionItem).filter(ActionItem.id == action_item_id).first()
        if not action:
            raise HTTPException(status_code=404, detail='Action item not found.')
        for field, value in payload.items():
            if hasattr(action, field):
                setattr(action, field, value)
        self.db.commit()
        self.db.refresh(action)
        return action

    def delete_action_item(self, action_item_id: int):
        action = self.db.query(ActionItem).filter(ActionItem.id == action_item_id).first()
        if not action:
            raise HTTPException(status_code=404, detail='Action item not found.')
        self.db.delete(action)
        self.db.commit()
        return True

    def delete_meeting(self, meeting_id: int):
        meeting = self.get_meeting(meeting_id)
        self.db.delete(meeting)
        self.db.commit()
        return True

    def serialize_meeting(self, meeting):
        return {
            'id': meeting.id,
            'title': meeting.title,
            'original_filename': meeting.original_filename,
            'file_type': meeting.file_type,
            'duration': meeting.duration,
            'status': meeting.status,
            'created_at': meeting.created_at.isoformat() if meeting.created_at else None,
            'summary': meeting.summary,
            'transcript': meeting.transcript,
            'detailed_summary': meeting.detailed_summary,
            'sentiment': meeting.sentiment,
            'action_items': [
                {
                    'id': item.id,
                    'description': item.description,
                    'assignee': item.assignee,
                    'deadline': item.deadline,
                    'priority': item.priority,
                    'status': item.status,
                } for item in meeting.actions
            ],
            'decisions': [
                {
                    'id': item.id,
                    'decision': item.decision,
                    'context': item.context,
                    'source_time': item.source_time,
                } for item in meeting.decisions
            ],
            'topics': [topic.name for topic in meeting.topics],
            'questions': [
                {
                    'id': item.id,
                    'question': item.question,
                    'answer': item.answer,
                } for item in meeting.questions
            ],
            'segments': [
                {
                    'id': segment.id,
                    'speaker': segment.speaker,
                    'start_time': segment.start_time,
                    'end_time': segment.end_time,
                    'text': segment.text,
                } for segment in meeting.transcript_segments
            ],
        }
