"""Text normalization utilities for user input and FAQ content."""

import re

STOPWORDS = {
    "a",
    "an",
    "the",
    "is",
    "are",
    "am",
    "was",
    "were",
    "to",
    "for",
    "of",
    "on",
    "in",
    "my",
    "your",
    "do",
    "does",
    "can",
    "i",
    "you",
}


def preprocess(text: str | None) -> str:
    """Lowercase, strip punctuation, and remove light stopwords."""
    if not text:
        return ""

    text = text.lower()
    text = re.sub(r"[^\w\s]", "", text)
    tokens = text.split()
    filtered_tokens = [token for token in tokens if token not in STOPWORDS]
    return " ".join(filtered_tokens)