"""Dataset loading helpers with support for malformed or mixed JSON input."""

import json


def _extract_json_chunks(raw_text: str):
    decoder = json.JSONDecoder()
    idx = 0
    parsed_chunks = []

    while idx < len(raw_text):
        while idx < len(raw_text) and raw_text[idx].isspace():
            idx += 1
        if idx >= len(raw_text):
            break

        try:
            chunk, next_idx = decoder.raw_decode(raw_text, idx)
            parsed_chunks.append(chunk)
            idx = next_idx
        except json.JSONDecodeError:
            # Move forward one character and keep scanning for the next valid JSON chunk.
            idx += 1

    return parsed_chunks


def _normalize_chunk(chunk):
    if isinstance(chunk, list):
        return chunk
    if isinstance(chunk, dict):
        return [chunk]
    return []


def load_faq(path):
    """Load FAQ rows from a clean or mixed-format JSON file."""
    with open(path, "r", encoding="utf-8") as f:
        raw_text = f.read()

    try:
        parsed = json.loads(raw_text)
        raw_data = _normalize_chunk(parsed)
    except json.JSONDecodeError:
        chunks = _extract_json_chunks(raw_text)
        raw_data = []
        for chunk in chunks:
            raw_data.extend(_normalize_chunk(chunk))

    normalized_rows = []
    seen = set()
    for item in raw_data:
        if not isinstance(item, dict) or "answer" not in item:
            continue

        answer = item["answer"].strip() if isinstance(item["answer"], str) else str(item["answer"])
        if "questions" in item:
            for question in item["questions"]:
                if not isinstance(question, str):
                    continue
                question = question.strip()
                if not question:
                    continue
                key = (question.lower(), answer.lower())
                if key in seen:
                    continue
                seen.add(key)
                normalized_rows.append({"question": question, "answer": answer})
        elif "question" in item and isinstance(item["question"], str):
            question = item["question"].strip()
            if question:
                key = (question.lower(), answer.lower())
                if key not in seen:
                    seen.add(key)
                    normalized_rows.append({"question": question, "answer": answer})

    return normalized_rows