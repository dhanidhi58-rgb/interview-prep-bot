"""Tests for the Mock AI provider and provider factory fallback."""
from ai.mock_provider import MockProvider
from ai.factory import get_ai_provider
from ai.base import GeneratedQuestion, EvaluationResult


def test_mock_provider_generates_question():
    provider = MockProvider()
    q = provider.generate_question(
        role="Python Developer",
        experience="Fresher",
        technology="Python",
        interview_type="Technical",
        difficulty="Easy",
        previous_questions=[],
    )
    assert isinstance(q, GeneratedQuestion)
    assert len(q.question) > 0


def test_mock_provider_avoids_repeating_questions_when_possible():
    provider = MockProvider()
    asked = []
    for _ in range(5):
        q = provider.generate_question(
            role="Python Developer",
            experience="Fresher",
            technology="Python",
            interview_type="Technical",
            difficulty="Easy",
            previous_questions=asked,
        )
        asked.append(q.question)
    # With enough Easy-difficulty Python questions in the bank, we expect
    # at least some variety across 5 draws.
    assert len(set(asked)) >= 2


def test_mock_provider_evaluates_empty_answer_as_zero():
    provider = MockProvider()
    result = provider.evaluate_answer(
        question="What is a list?",
        answer="",
        role="Python Developer",
        experience="Fresher",
        difficulty="Easy",
    )
    assert isinstance(result, EvaluationResult)
    assert result.score == 0


def test_mock_provider_evaluates_substantive_answer_positively():
    provider = MockProvider()
    result = provider.evaluate_answer(
        question="What is a list?",
        answer=(
            "A list in Python is a mutable, ordered collection of items. "
            "For example, my_list = [1, 2, 3] because it lets you store "
            "multiple values which means you can iterate over them easily."
        ),
        role="Python Developer",
        experience="Fresher",
        difficulty="Easy",
    )
    assert result.score >= 5


def test_factory_falls_back_to_mock_without_api_keys(monkeypatch):
    monkeypatch.setenv("AI_PROVIDER", "openai")
    monkeypatch.setenv("OPENAI_API_KEY", "")
    provider = get_ai_provider()
    assert provider.name == "mock"
