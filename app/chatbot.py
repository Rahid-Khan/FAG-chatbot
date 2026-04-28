"""High-level chatbot service that coordinates retrieval and response policy."""

from __future__ import annotations

from app.retrieval import RetrievalEngine
from app.config import get_settings
from utils.file_loader import load_faq
from utils.logger import log_query


class Chatbot:
    """Application service combining the dataset, retriever, and fallback logic."""

    def __init__(self):
        self.settings = get_settings()
        self.faq_data = load_faq(self.settings.faq_data_path)
        self.engine = RetrievalEngine(
            self.faq_data,
            model_name=self.settings.embedding_model,
            top_k=self.settings.top_k,
        )
        self.threshold = self.settings.confidence_threshold

    @staticmethod
    def _confidence_bucket(score: float) -> str:
        """Map score ranges to a human-readable confidence bucket."""
        if score >= 0.8:
            return "high"
        if score >= 0.5:
            return "medium"
        return "low"

    def get_response(self, user_input: str, *, request_id: str | None = None):
        """Return response metadata with a safe fallback below threshold."""
        response, score, suggestions = self.engine.retrieve(user_input)

        if score < self.threshold:
            fallback = (
                "I'm not sure about that yet. Try rephrasing your question. "
                f"You can ask something like: {', '.join(suggestions[:3])}"
            )
            log_query(user_input, fallback, score, request_id=request_id)
            return {
                "response": fallback,
                "score": score,
                "matched": False,
                "suggestions": suggestions[:3],
                "confidence": self._confidence_bucket(score),
            }

        log_query(user_input, response, score, request_id=request_id)
        return {
            "response": response,
            "score": score,
            "matched": True,
            "suggestions": suggestions[:3],
            "confidence": self._confidence_bucket(score),
        }