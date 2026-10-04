import subprocess
from pathlib import Path

VIDEO_EXTENSIONS = {'.mp4', '.webm'}


def extract_audio_if_needed(video_path: str, output_path: str | None = None) -> str:
    input_path = Path(video_path)
    if input_path.suffix.lower() not in VIDEO_EXTENSIONS:
        return str(input_path)

    destination = Path(output_path) if output_path else input_path.with_suffix('.mp3')
    try:
        subprocess.run(
            [
                'ffmpeg',
                '-y',
                '-i',
                str(input_path),
                '-vn',
                '-acodec',
                'libmp3lame',
                '-q:a',
                '2',
                str(destination),
            ],
            check=True,
            capture_output=True,
            text=True,
        )
    except (FileNotFoundError, subprocess.CalledProcessError):
        return str(input_path)
    return str(destination)
