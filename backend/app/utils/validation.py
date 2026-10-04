from pathlib import Path

ALLOWED_EXTENSIONS = {'.mp3', '.wav', '.m4a', '.mp4', '.webm', '.txt', '.md'}


def validate_upload(file_obj, max_size_mb: int = 200) -> str:
    if file_obj is None:
        raise ValueError('Missing file upload.')
    filename = getattr(file_obj, 'filename', '') or ''
    extension = Path(filename).suffix.lower()
    if extension not in ALLOWED_EXTENSIONS:
        raise ValueError('Unsupported file type. Allowed: MP3, WAV, M4A, MP4, WEBM, TXT, MD.')
    size = getattr(file_obj, 'size', None)
    if size is None:
        size = 0
    if size > max_size_mb * 1024 * 1024:
        raise ValueError(f'File is too large. Maximum allowed size is {max_size_mb} MB.')
    return extension
