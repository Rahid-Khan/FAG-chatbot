import unittest
from unittest.mock import patch

from app.preprocessing import preprocess
from app.retrieval import RetrievalEngine


class PreprocessingTests(unittest.TestCase):
    def test_preprocess_removes_punctuation_and_stopwords(self):
        result = preprocess("Can I reset my password?")
        self.assertEqual(result, "reset password")

    def test_preprocess_handles_empty_input(self):
        self.assertEqual(preprocess(""), "")
        self.assertEqual(preprocess(None), "")


class FakeTensorValue:
    def __init__(self, value):
        self.value = value

    def item(self):
        return self.value


class FakeSimilarityRow:
    def topk(self, k):
        return (
            [FakeTensorValue(0.93), FakeTensorValue(0.52)][:k],
            [FakeTensorValue(0), FakeTensorValue(1)][:k],
        )


class RetrievalEngineTests(unittest.TestCase):
    @patch("app.retrieval.util.cos_sim", return_value=[FakeSimilarityRow()])
    @patch("app.retrieval.SentenceTransformer")
    def test_retrieve_returns_answer_score_and_suggestions(self, mock_transformer, mock_cos_sim):
        model = mock_transformer.return_value
        model.encode.side_effect = ["question_embeddings", "user_embedding"]

        engine = RetrievalEngine(
            [
                {"question": "How can I reset my password?", "answer": "Use forgot password."},
                {"question": "How can I track my order?", "answer": "Check order history."},
            ],
            model_name="test-model",
            top_k=2,
        )

        answer, score, suggestions = engine.retrieve("reset password")

        self.assertEqual(answer, "Use forgot password.")
        self.assertAlmostEqual(score, 0.93)
        self.assertEqual(
            suggestions,
            ["How can I reset my password?", "How can I track my order?"],
        )


if __name__ == "__main__":
    unittest.main()
