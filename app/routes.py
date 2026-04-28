"""HTTP routes for the FAQ chatbot application."""

from __future__ import annotations

import time
import uuid

from flask import Blueprint, render_template, request

from app.api import error_response, success_response
from app.chatbot import Chatbot
from utils.logger import log_request

main = Blueprint('main', __name__)
_bot: Chatbot | None = None


def get_bot() -> Chatbot:
    """Lazily initialize the chatbot service."""
    global _bot
    if _bot is None:
        _bot = Chatbot()
    return _bot


@main.route("/")
def index():
    """Render the main chat interface."""
    return render_template("index.html")


@main.route("/chat", methods=["POST"])
def chat():
    """Handle chat requests and return a standardized JSON response."""
    started_at = time.perf_counter()
    request_id = str(uuid.uuid4())
    payload = request.get_json(silent=True) or {}
    user_input = payload.get("message", "").strip()
    if not user_input:
        duration_ms = (time.perf_counter() - started_at) * 1000
        log_request("/chat", "POST", 400, duration_ms, request_id=request_id)
        return error_response(
            "Please send a message in the 'message' field.",
            code="empty_message",
            status_code=400,
            meta={"request_id": request_id},
        )

    result = get_bot().get_response(user_input, request_id=request_id)
    duration_ms = (time.perf_counter() - started_at) * 1000
    log_request("/chat", "POST", 200, duration_ms, request_id=request_id)
    return success_response(
        result["response"],
        meta={
            "request_id": request_id,
            "score": round(result["score"], 4),
            "matched": result["matched"],
            "confidence": result["confidence"],
            "suggestions": result["suggestions"],
            "latency_ms": round(duration_ms, 2),
        },
    )