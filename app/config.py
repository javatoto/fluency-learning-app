"""
Application configuration using pydantic-settings.
"""
from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    # Application
    SECRET_KEY: str = "dev-secret-key-change-in-production"
    DEBUG: bool = True

    # Database
    DATABASE_URL: str = "sqlite:///./fluency.db"

    # OpenAI
    OPENAI_API_KEY: Optional[str] = None

    # Audio Settings
    MAX_RECORDING_DURATION: int = 60
    MAX_FILE_SIZE_MB: int = 5
    AUDIO_STORAGE_PATH: str = "./audio_files"

    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()
