"""
Central application configuration.

All values are read from environment variables (via .env). Nothing here
is hard-coded as a secret. If required values are missing, safe defaults
are used so the application can still run in Demo Mode.
"""
import os
from pathlib import Path
from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent.parent
load_dotenv(BASE_DIR / ".env")

LOG_DIR = BASE_DIR / "logs"
STORAGE_DIR = BASE_DIR / "storage"
LOG_DIR.mkdir(exist_ok=True)
STORAGE_DIR.mkdir(exist_ok=True)


def _clean(value):
    if value is None:
        return ""
    return value.strip()


class Settings:
    AI_PROVIDER: str = _clean(os.getenv("AI_PROVIDER", "mock")).lower() or "mock"
    OPENAI_API_KEY: str = _clean(os.getenv("OPENAI_API_KEY", ""))
    ANTHROPIC_API_KEY: str = _clean(os.getenv("ANTHROPIC_API_KEY", ""))
    MODEL_NAME: str = _clean(os.getenv("MODEL_NAME", ""))
    DATABASE_URL: str = _clean(
        os.getenv("DATABASE_URL", f"sqlite:///{STORAGE_DIR / 'interview_prep.db'}")
    )

    DEFAULT_DIFFICULTY: str = "Medium"
    DEFAULT_QUESTION_COUNT: int = 10

    LOG_FILE: Path = LOG_DIR / "app.log"

    @classmethod
    def effective_provider(cls) -> str:
        """
        Decide which AI provider is actually usable.
        Falls back to 'mock' automatically if the requested provider
        has no valid API key configured. This guarantees the app is
        always usable, per the Demo Mode requirement.
        """
        provider = cls.AI_PROVIDER
        if provider == "openai" and not cls.OPENAI_API_KEY:
            return "mock"
        if provider == "anthropic" and not cls.ANTHROPIC_API_KEY:
            return "mock"
        if provider not in ("openai", "anthropic", "mock"):
            return "mock"
        return provider

    @classmethod
    def masked_key(cls, key: str) -> str:
        if not key:
            return "(not set)"
        if len(key) <= 8:
            return "*" * len(key)
        return key[:4] + "*" * (len(key) - 8) + key[-4:]


settings = Settings()
