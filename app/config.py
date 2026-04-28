"""Application configuration with environment-aware defaults."""

from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parent.parent


def _get_bool(name: str, default: bool) -> bool:
    return os.getenv(name, str(default)).strip().lower() in {"1", "true", "yes", "on"}


def _get_float(name: str, default: float) -> float:
    raw = os.getenv(name)
    if raw is None:
        return default
    try:
        return float(raw)
    except ValueError as exc:
        raise ValueError(f"Environment variable {name} must be a float.") from exc


@dataclass(frozen=True)
class Settings:
    faq_data_path: Path
    embedding_model: str
    confidence_threshold: float
    top_k: int
    flask_host: str
    flask_port: int
    flask_debug: bool
    log_level: str

    def validate(self) -> None:
        """Validate settings at startup with explicit failure messages."""
        if not self.faq_data_path.exists():
            raise FileNotFoundError(f"FAQ dataset not found: {self.faq_data_path}")
        if not 0.0 <= self.confidence_threshold <= 1.0:
            raise ValueError("CONFIDENCE_THRESHOLD must be between 0.0 and 1.0.")
        if self.top_k < 1:
            raise ValueError("TOP_K must be at least 1.")
        if self.flask_port < 1 or self.flask_port > 65535:
            raise ValueError("FLASK_PORT must be between 1 and 65535.")


def get_settings() -> Settings:
    """Return validated application settings."""
    faq_relative_path = os.getenv("FAQ_DATA_PATH", "data/faq.json")
    faq_data_path = (PROJECT_ROOT / faq_relative_path).resolve()
    settings = Settings(
        faq_data_path=faq_data_path,
        embedding_model=os.getenv("EMBEDDING_MODEL", "all-MiniLM-L6-v2"),
        confidence_threshold=_get_float("CONFIDENCE_THRESHOLD", 0.5),
        top_k=int(os.getenv("TOP_K", "3")),
        flask_host=os.getenv("FLASK_HOST", "127.0.0.1"),
        flask_port=int(os.getenv("FLASK_PORT", "5000")),
        flask_debug=_get_bool("FLASK_DEBUG", True),
        log_level=os.getenv("LOG_LEVEL", "INFO").upper(),
    )
    settings.validate()
    return settings
