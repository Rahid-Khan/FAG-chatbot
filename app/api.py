"""API response helpers for consistent JSON contracts."""

from typing import Any

from flask import jsonify


def success_response(response_text: str, *, meta: dict[str, Any] | None = None, status_code: int = 200):
    """Build a standard success payload."""
    payload = {
        "success": True,
        "response": response_text,
        "meta": meta or {},
        "error": None,
    }
    return jsonify(payload), status_code


def error_response(message: str, *, code: str, status_code: int, meta: dict[str, Any] | None = None):
    """Build a standard error payload."""
    payload = {
        "success": False,
        "response": "",
        "meta": meta or {},
        "error": {"code": code, "message": message},
    }
    return jsonify(payload), status_code
