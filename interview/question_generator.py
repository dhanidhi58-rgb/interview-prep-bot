"""
Wraps an AIProvider to generate the next interview question while
avoiding repeats and honoring the adaptive-difficulty setting.
"""
from typing import List, Optional
from ai.base import AIProvider, GeneratedQuestion


class QuestionGenerator:
    def __init__(self, provider: AIProvider):
        self.provider = provider

    def next_question(
        self,
        role: str,
        experience: str,
        technology: str,
        interview_type: str,
        difficulty: str,
        previous_questions: List[str],
        performance_hint: Optional[str] = None,
    ) -> GeneratedQuestion:
        try:
            return self.provider.generate_question(
                role=role,
                experience=experience,
                technology=technology,
                interview_type=interview_type,
                difficulty=difficulty,
                previous_questions=previous_questions,
                performance_hint=performance_hint,
            )
        except Exception:
            # Safe fallback: never let question generation crash the interview.
            from ai.mock_provider import MockProvider

            return MockProvider().generate_question(
                role, experience, technology, interview_type, difficulty, previous_questions
            )
