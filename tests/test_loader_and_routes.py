import os
import tempfile
import unittest
from unittest.mock import patch

from app import create_app
from utils.file_loader import load_faq


class FileLoaderTests(unittest.TestCase):
    def test_load_faq_handles_mixed_json_formats(self):
        content = """
[
  {"questions": ["How can I reset my password?"], "answer": "Use forgot password."}
]
{"question": "How can I track my order?", "answer": "Check order history."}
"""
        with tempfile.NamedTemporaryFile("w", suffix=".json", delete=False, encoding="utf-8") as tmp:
            tmp.write(content)
            tmp_path = tmp.name

        try:
            rows = load_faq(tmp_path)
        finally:
            os.remove(tmp_path)

        questions = {row["question"] for row in rows}
        self.assertIn("How can I reset my password?", questions)
        self.assertIn("How can I track my order?", questions)


class RouteTests(unittest.TestCase):
    @patch("app.routes.get_bot")
    def test_chat_endpoint_success(self, mock_get_bot):
        mock_get_bot.return_value.get_response.return_value = {
            "response": "Sample answer",
            "score": 0.88,
            "matched": True,
            "confidence": "high",
            "suggestions": ["Reset password"],
        }
        app = create_app()
        client = app.test_client()

        response = client.post("/chat", json={"message": "hello"})
        payload = response.get_json()

        self.assertEqual(response.status_code, 200)
        self.assertTrue(payload["success"])
        self.assertEqual(payload["response"], "Sample answer")
        self.assertEqual(payload["meta"]["matched"], True)
        self.assertEqual(payload["meta"]["confidence"], "high")
        self.assertIn("request_id", payload["meta"])

    def test_chat_endpoint_rejects_empty_message(self):
        app = create_app()
        client = app.test_client()

        response = client.post("/chat", json={"message": "   "})
        payload = response.get_json()

        self.assertEqual(response.status_code, 400)
        self.assertFalse(payload["success"])
        self.assertEqual(payload["error"]["code"], "empty_message")
        self.assertIn("Please send a message", payload["error"]["message"])

    def test_not_found_route_returns_standard_error_schema(self):
        app = create_app()
        client = app.test_client()

        response = client.get("/missing")
        payload = response.get_json()

        self.assertEqual(response.status_code, 404)
        self.assertFalse(payload["success"])
        self.assertEqual(payload["error"]["code"], "not_found")

    def test_index_route_renders_template(self):
        app = create_app()
        client = app.test_client()

        response = client.get("/")

        self.assertEqual(response.status_code, 200)
        self.assertIn(b"FAQ Assistant", response.data)


if __name__ == "__main__":
    unittest.main()
