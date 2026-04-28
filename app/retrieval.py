"""Semantic retrieval engine for FAQ matching."""

from __future__ import annotations

import warnings

from sentence_transformers import SentenceTransformer, util
from app.preprocessing import preprocess

# Suppress noisy HF auth warning for local/dev use.
warnings.filterwarnings(
    "ignore",
    message=r"You are sending unauthenticated requests to the HF Hub.*",
)


class RetrievalEngine:
    """Embedding-based FAQ retriever."""

    def __init__(self, faq_data, model_name: str, top_k: int = 3):
        self.model = SentenceTransformer(model_name)
        self.top_k = top_k

        self.questions = [item["question"] for item in faq_data]
        self.answers = [item["answer"] for item in faq_data]
        self.processed_questions = [preprocess(question) for question in self.questions]
        self.question_embeddings = self.model.encode(self.processed_questions, convert_to_tensor=True)

    def retrieve(self, user_input: str):
        """Return best answer, score, and suggested nearby questions."""
        processed_input = preprocess(user_input)
        user_embedding = self.model.encode(processed_input, convert_to_tensor=True)
        similarities = util.cos_sim(user_embedding, self.question_embeddings)[0]

        top_values, top_indices = similarities.topk(k=min(self.top_k, len(self.questions)))
        best_idx = int(top_indices[0].item())
        best_score = float(top_values[0].item())

        suggestions = [self.questions[int(idx.item())] for idx in top_indices]
        return self.answers[best_idx], best_score, suggestions