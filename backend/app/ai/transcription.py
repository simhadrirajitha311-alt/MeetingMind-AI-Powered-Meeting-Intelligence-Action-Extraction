import re
from pathlib import Path

from backend.app.utils.audio import extract_audio_if_needed


class TranscriptionProvider:
    def transcribe(self, audio_path: str):
        raise NotImplementedError


class DemoTranscriptionProvider(TranscriptionProvider):
    def transcribe(self, audio_path: str):
        path = Path(audio_path)
        stem = path.stem.replace('-', ' ').replace('_', ' ')
        title = stem.title()
        transcript = (
            'Speaker 1: We agreed to launch the project next Friday and keep the workstream aligned. '
            'Speaker 2: I will finalize the marketing checklist and share it by Thursday. '
            'Speaker 1: We also need budget approval before we sign off on the plan. '
            'Speaker 2: I will review the launch risks with the team and confirm the final timeline.'
        )
        if 'budget' in stem.lower():
            transcript = (
                'Speaker 1: We need to review the budget and confirm the operating plan before the launch. '
                'Speaker 2: I will prepare the final cost summary by Thursday. '
                'Speaker 1: The budget approval is the main dependency for the schedule. '
                'Speaker 2: Once approved, we can move forward with the launch checklist.'
            )
        segments = []
        speaker_pattern = re.compile(r'(Speaker\s*\d+):(.*?)(?=(Speaker\s*\d+:)|$)', re.DOTALL)
        matches = speaker_pattern.findall(transcript)
        for index, (speaker, text) in enumerate(matches):
            cleaned = ' '.join(text.strip().split())
            segments.append({
                'speaker': speaker,
                'start_time': float(index * 10),
                'end_time': float(index * 10 + 12),
                'text': cleaned,
            })
        if not segments:
            segments = [{
                'speaker': 'Speaker 1',
                'start_time': 0.0,
                'end_time': 12.0,
                'text': 'We agreed to launch the project next Friday and keep the workstream aligned.',
            }, {
                'speaker': 'Speaker 2',
                'start_time': 12.0,
                'end_time': 24.0,
                'text': 'I will finalize the marketing checklist and share it by Thursday.',
            }]
        return {'segments': segments, 'title': title, 'mode': 'demo'}


def transcribe_audio_file(audio_path: str):
    extracted = extract_audio_if_needed(audio_path)
    provider = DemoTranscriptionProvider()
    return provider.transcribe(extracted)
