"""Tests for the Evaluator wrapper and EvaluationResult validation."""
import pytest
from pydantic import ValidationError

from ai.base import EvaluationResult
from ai.mock_provider import MockProvider
from interview.evaluator import Evaluator


def test_evaluation_result_validates_and_clamps_types():
    result = EvaluationResult(
        score="7",  # string coerced to int
        technical_accuracy=7.6,  # float coerced/rounded
        relevance=8,
        completeness=6,
        clarity=7,
    )
    assert result.score == 7
    assert result.technical_accuracy == 8


def test_evaluation_result_rejects_out_of_range_score():
    with pytest.raises(ValidationError):
        EvaluationResult(
            score=15,
            technical_accuracy=5,
            relevance=5,
            completeness=5,
            clarity=5,
        )


def test_evaluator_uses_mock_provider_successfully():
    evaluator = Evaluator(MockProvider())
    result = evaluator.evaluate(
        question="Explain OOP.",
        answer="OOP stands for Object Oriented Programming, based on classes and objects.",
        role="Python Developer",
        experience="Fresher",
        difficulty="Easy",
    )
    assert 0 <= result.score <= 10


class _AlwaysFailsProvider:
    name = "broken"

    def evaluate_answer(self, *args, **kwargs):
        raise RuntimeError("simulated provider failure")

    def generate_question(self, *args, **kwargs):
        raise RuntimeError("simulated provider failure")


def test_evaluator_falls_back_to_mock_on_provider_failure():
    evaluator = Evaluator(_AlwaysFailsProvider())
    result = evaluator.evaluate(
        question="Explain OOP.",
        answer="OOP is about classes and objects.",
        role="Python Developer",
        experience="Fresher",
        difficulty="Easy",
    )
    assert 0 <= result.score <= 10
