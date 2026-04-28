"""Structured logging helpers for the chatbot application."""

from __future__ import annotations

import json
import logging
from pathlib import Path
from typing import Any


LOG_DIR = Path("logs")
LOG_FILE = LOG_DIR / "chatbot.log"


def configure_logging(level: str = "INFO") -> logging.Logger:
    """Configure the application logger once and return it."""
    LOG_DIR.mkdir(exist_ok=True)
    logger = logging.getLogger("faq_chatbot")
    logger.setLevel(getattr(logging, level.upper(), logging.INFO))
    logger.propagate = False

    if not logger.handlers:
        handler = logging.FileHandler(LOG_FILE, encoding="utf-8")
        handler.setFormatter(logging.Formatter("%(asctime)s %(levelname)s %(message)s"))
        logger.addHandler(handler)

    return logger


def get_logger() -> logging.Logger:
    """Return the configured application logger."""
    return logging.getLogger("faq_chatbot")


def _serialize_event(event_type: str, **payload: Any) -> str:
    return json.dumps({"event": event_type, **payload}, ensure_ascii=True)


def log_query(user_input: str, response: str, score: float, *, request_id: str | None = None) -> None:
    """Log chatbot answer details."""
    get_logger().info(
        _serialize_event(
            "chat_query",
            request_id=request_id,
            user_input=user_input,
            response=response,
            score=round(score, 4),
        )
    )


def log_request(path: str, method: str, status_code: int, duration_ms: float, *, request_id: str) -> None:
    """Log request metadata."""
    get_logger().info(
        _serialize_event(
            "http_request",
            request_id=request_id,
            path=path,
            method=method,
            status_code=status_code,
            duration_ms=round(duration_ms, 2),
        )
    )