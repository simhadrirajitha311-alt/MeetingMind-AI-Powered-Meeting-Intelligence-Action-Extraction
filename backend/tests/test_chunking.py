from backend.app.utils.chunking import chunk_transcript


segments = [
    {'speaker': 'Speaker 1', 'start_time': 0, 'end_time': 10, 'text': 'We will launch the project next Friday. The team agreed to finalize the budget by Thursday.'},
    {'speaker': 'Speaker 2', 'start_time': 10, 'end_time': 20, 'text': 'I will handle the marketing sprint and keep the launch checklist updated.'},
]


def test_chunk_transcript_preserves_metadata():
    chunks = chunk_transcript(segments, max_chars=80, overlap=10)
    assert len(chunks) > 0
    assert 'speaker' in chunks[0]
    assert 'start_time' in chunks[0]
    assert 'text' in chunks[0]
