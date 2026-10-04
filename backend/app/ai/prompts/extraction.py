EXTRACTION_PROMPT = """
Extract action items from the meeting transcript.
Return JSON with these keys only:
[
  {
    "task": "...",
    "assignee": "...",
    "deadline": "...",
    "priority": "low|medium|high",
    "evidence": "..."
  }
]
Do not infer owners that are not supported by the text.

Transcript:
{transcript}
"""
