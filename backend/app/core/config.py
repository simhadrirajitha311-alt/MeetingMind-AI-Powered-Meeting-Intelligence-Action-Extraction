from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict

BASE_DIR = Path(__file__).resolve().parents[3]


class Settings(BaseSettings):
    app_env: str = 'development'
    database_url: str = f'sqlite:///{BASE_DIR / "meetingmind.db"}'
    llm_api_key: str = ''
    llm_model: str = 'gpt-4o-mini'
    llm_base_url: str = ''
    embedding_model: str = 'all-MiniLM-L6-v2'
    max_upload_size_mb: int = 200
    cors_origins: str = 'http://localhost:5173'

    model_config = SettingsConfigDict(
        env_file='.env',
        env_file_encoding='utf-8',
        extra='ignore',
        case_sensitive=False,
    )


settings = Settings()
