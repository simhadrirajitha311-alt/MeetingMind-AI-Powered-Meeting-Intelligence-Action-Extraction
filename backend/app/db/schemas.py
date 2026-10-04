from __future__ import annotations

from typing import Any, Literal

from pydantic import BaseModel, Field


class TranscriptSegmentSchema(BaseModel):
    speaker: str = 'Speaker 1'
    start_time: float = 0.0
    end_time: float = 0.0
    text: str


class ActionItemSchema(BaseModel):
    task: str
    assignee: str | None = None
    deadline: str | None = None
    priority: Literal['low', 'medium', 'high'] = 'medium'
    evidence: str | None = None


class DecisionSchema(BaseModel):
    decision: str
    context: str | None = None
    source_timestamp: float | None = None


class MeetingSummarySchema(BaseModel):
    executive_summary: str = ''
    detailed_summary: str = ''
    key_points: list[str] = Field(default_factory=list)
    decisions: list[DecisionSchema] = Field(default_factory=list)
    action_items: list[ActionItemSchema] = Field(default_factory=list)
    deadlines: list[str] = Field(default_factory=list)
    questions: list[dict[str, str]] = Field(default_factory=list)
    risks: list[str] = Field(default_factory=list)
    topics: list[str] = Field(default_factory=list)
    sentiment: dict[str, Any] = Field(default_factory={'overall': 'neutral', 'confidence': 0.0})


class SearchResultSchema(BaseModel):
    text: str
    speaker: str
    start_time: float
    score: float


class AskResponseSchema(BaseModel):
    answer: str
    sources: list[dict[str, Any]]


class MeetingDetailSchema(BaseModel):
    id: int
    title: str
    original_filename: str | None = None
    file_type: str | None = None
    duration: float = 0.0
    status: str = 'uploaded'
    summary: str | None = None
    detailed_summary: str | None = None
    sentiment: str | None = 'neutral'
    transcript: str = ''
    analysis: dict[str, Any] | None = None
