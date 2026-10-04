import re


def chunk_transcript(segments, max_chars=500, overlap=60):
    chunks = []
    if not segments:
        return chunks

    buffer = []
    buffer_length = 0
    speaker = segments[0].get('speaker', 'Speaker 1')
    start_time = segments[0].get('start_time', 0.0)
    end_time = segments[0].get('end_time', 0.0)

    def flush():
        nonlocal buffer, buffer_length, speaker, start_time, end_time
        text = ' '.join(part.strip() for part in buffer if part.strip())
        if not text:
            return
        chunks.append({
            'speaker': speaker,
            'start_time': start_time,
            'end_time': end_time,
            'text': text,
        })
        buffer = []
        buffer_length = 0

    for segment in segments:
        sentence_parts = re.split(r'(?<=[.!?])\s+', (segment.get('text', '') or '').strip())
        for sentence in sentence_parts:
            if not sentence:
                continue
            if buffer_length and buffer_length + len(sentence) > max_chars:
                flush()
            if not buffer:
                speaker = segment.get('speaker', 'Speaker 1')
                start_time = float(segment.get('start_time', 0.0))
            end_time = float(segment.get('end_time', segment.get('start_time', 0.0)))
            buffer.append(sentence)
            buffer_length += len(sentence)

    flush()
    return chunks
