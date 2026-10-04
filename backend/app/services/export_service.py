from __future__ import annotations

import json


def export_markdown(meeting):
    lines = [
        f'# {meeting.title}',
        '',
        f'- Date: {meeting.created_at.date() if meeting.created_at else "N/A"}',
        f'- Status: {meeting.status}',
        '',
        '## Executive Summary',
        '',
        meeting.summary or 'No summary available.',
        '',
        '## Key Decisions',
    ]
    for decision in meeting.decisions:
        lines.append(f'- {decision.decision}')
    lines.extend(['', '## Action Items'])
    for action in meeting.actions:
        lines.append(f'- {action.description} ({action.assignee or "Unassigned"})')
    lines.extend(['', '## Transcript'])
    for segment in meeting.transcript_segments:
        lines.append(f'- {segment.speaker} [{segment.start_time:.0f}s]: {segment.text}')
    return '\n'.join(lines)


def export_json(meeting):
    payload = {
        'title': meeting.title,
        'status': meeting.status,
        'summary': meeting.summary,
        'detailed_summary': meeting.detailed_summary,
        'sentiment': meeting.sentiment,
        'transcript': meeting.transcript,
        'decisions': [dict(id=item.id, decision=item.decision, context=item.context, source_time=item.source_time) for item in meeting.decisions],
        'action_items': [dict(id=item.id, description=item.description, assignee=item.assignee, deadline=item.deadline, priority=item.priority, status=item.status) for item in meeting.actions],
    }
    return json.dumps(payload, indent=2, ensure_ascii=False)
