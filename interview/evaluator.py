"""
Wraps an AIProvider to evaluate a candidate's answer, always
returning a validated EvaluationResult even if the live provider
fails (falls back to MockProvider so the interview never breaks).
"""
from ai.base import AIProvider, EvaluationResult


class Evaluator:
    def __init__(self, provider: AIProvider):
        self.provider = provider

    def evaluate(
        self, question: str, answer: str, role: str, experience: str, difficulty: str
    ) -> EvaluationResult:
        try:
            return self.provider.evaluate_answer(
                question=question,
                answer=answer,
                role=role,
                experience=experience,
                difficulty=difficulty,
            )
        except Exception:
            from ai.mock_provider import MockProvider

            return MockProvider().evaluate_answer(question, answer, role, experience, difficulty)
