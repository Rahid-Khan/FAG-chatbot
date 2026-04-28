import unittest
from unittest.mock import patch

from app.chatbot import Chatbot


class StubEngine:
    def __init__(self, response, score, suggestions):
        self._response = response
        self._score = score
        self._suggestions = suggestions

    def retrieve(self, user_input):
        return self._response, self._score, self._suggestions


class ChatbotBehaviorTests(unittest.TestCase):
    def test_returns_best_answer_above_threshold(self):
        bot = Chatbot.__new__(Chatbot)
        bot.threshold = 0.5
        bot.engine = StubEngine("Reset using forgot password.", 0.91, ["Reset password"])

        with patch("app.chatbot.log_query") as mock_log:
            result = bot.get_response("I forgot my password")

        self.assertEqual(result["response"], "Reset using forgot password.")
        self.assertTrue(result["matched"])
        self.assertEqual(result["suggestions"], ["Reset password"])
        self.assertEqual(result["confidence"], "high")
        mock_log.assert_called_once()

    def test_returns_fallback_below_threshold(self):
        bot = Chatbot.__new__(Chatbot)
        bot.threshold = 0.5
        bot.engine = StubEngine("unused", 0.2, ["How can I reset my password?", "How can I track my order?"])

        with patch("app.chatbot.log_query") as mock_log:
            result = bot.get_response("some unknown query")

        self.assertIn("I'm not sure", result["response"])
        self.assertIn("How can I reset my password?", result["response"])
        self.assertFalse(result["matched"])
        self.assertEqual(len(result["suggestions"]), 2)
        self.assertEqual(result["confidence"], "low")
        mock_log.assert_called_once()

    def test_limits_suggestions_to_top_three(self):
        bot = Chatbot.__new__(Chatbot)
        bot.threshold = 0.9
        bot.engine = StubEngine("unused", 0.1, ["q1", "q2", "q3", "q4"])

        result = bot.get_response("unknown")

        self.assertEqual(result["suggestions"], ["q1", "q2", "q3"])


if __name__ == "__main__":
    unittest.main()
