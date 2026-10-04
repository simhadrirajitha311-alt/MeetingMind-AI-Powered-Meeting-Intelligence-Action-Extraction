import json
import re
from typing import Any

from backend.app.ai.prompts.analysis import ANALYSIS_PROMPT
from backend.app.ai.prompts.rag import RAG_PROMPT
from backend.app.core.config import settings


class DemoLLMProvider:
    def generate_analysis(self, transcript: str) -> dict[str, Any]:
        text = transcript.lower()
        action_items = []
        decisions = []
        deadlines = []
        topics = []

        if 'launch' in text:
            decisions.append({
                'decision': 'Launch the product next Friday.',
                'context': 'The team agreed on the launch timeline during the meeting.',
                'source_timestamp': 40.0,
            })
            action_items.append({
                'task': 'Prepare the launch checklist',
                'assignee': 'Speaker 2',
                'deadline': 'Thursday',
                'priority': 'high',
                'evidence': 'Speaker 2 agreed to prepare the launch checklist before Thursday.',
            })
            deadlines.append('Thursday: finalize launch checklist')
            deadlines.append('Friday: public launch')
        if 'budget' in text:
            topics.append('Budget approval')
        if 'marketing' in text:
            topics.append('Marketing strategy')
        if 'roadmap' in text:
            topics.append('Roadmap planning')
        if not topics:
            topics = ['Project planning', 'Execution follow-up']

        if not action_items:
            action_items = [{
                'task': 'Review the project follow-up notes',
                'assignee': 'Speaker 1',
                'deadline': 'Next meeting',
                'priority': 'medium',
                'evidence': 'The transcript mentions a follow-up task to review the final notes.',
            }]

        if not decisions:
            decisions = [{
                'decision': 'Proceed with the agreed next steps.',
                'context': 'The team confirmed there was no material disagreement in the transcript.',
                'source_timestamp': 20.0,
            }]

        return {
            'mode': 'demo',
            'executive_summary': 'The team aligned on the next launch milestones and confirmed follow-up work before the next review.',
            'detailed_summary': 'The discussion focused on launch timeline, budget alignment, and ownership for preparation tasks. The transcript indicates clear ownership for the next deliverables and a generally positive team posture.',
            'key_points': [
                'Team agreed on milestone timing.',
                'Ownership for follow-up actions was assigned.',
                'The group discussed risks and mitigation around launch readiness.',
            ],
            'decisions': decisions,
            'action_items': action_items,
            'deadlines': deadlines,
            'questions': [{
                'question': 'What is the next milestone?',
                'answer': 'The next milestone is the launch review on Friday.',
            }],
            'risks': ['Budget approval could affect schedule if delayed.', 'Launch readiness depends on final checklist completion.'],
            'topics': topics,
            'sentiment': {'overall': 'positive', 'confidence': 0.85},
        }

    def answer_question(self, question: str, context: str) -> dict[str, Any]:
        lower_question = question.lower()
        if 'launch' in lower_question or 'deadline' in lower_question:
            answer = 'The team aligned on a Friday launch and asked the team to complete the launch checklist before Thursday.'
        elif 'budget' in lower_question:
            answer = 'The transcript mentions budget approval as a dependency for launch readiness.'
        else:
            answer = "I couldn't find that information in this meeting."

        return {
            'answer': answer,
            'sources': [
                {'speaker': 'Speaker 1', 'start_time': 18.0, 'text': 'We agreed to launch on Friday and keep the budget review in motion.'},
                {'speaker': 'Speaker 2', 'start_time': 42.0, 'text': 'I will prepare the checklist before Thursday.'},
            ],
        }


class LLMProvider(DemoLLMProvider):
    def __init__(self, api_key: str | None = None, model: str | None = None, base_url: str | None = None):
        self.api_key = api_key or settings.llm_api_key
        self.model = model or settings.llm_model
        self.base_url = base_url or settings.llm_base_url

    def _parse_json(self, raw: str) -> dict:
        match = re.search(r'({.*})', raw, re.S)
        if match:
            return json.loads(match.group(1))
        return json.loads(raw)

    def generate_analysis(self, transcript: str) -> dict[str, Any]:
        if not self.api_key or not self.base_url:
            return super().generate_analysis(transcript)
        raise NotImplementedError('Remote LLM calls are intentionally unavailable in this demo setup.')

    def answer_question(self, question: str, context: str) -> dict[str, Any]:
        if not self.api_key or not self.base_url:
            return super().answer_question(question, context)
        raise NotImplementedError('Remote LLM calls are intentionally unavailable in this demo setup.')
