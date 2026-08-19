"""
Abstract base class every AI provider must implement, plus the
Pydantic models used to validate structured AI output everywhere
in the app. Keeping these here avoids circular imports between the
providers and the interview logic.
"""
from abc import ABC, abstractmethod
from typing import List, Optional
from pydantic import BaseModel, Field, field_validator


class EvaluationResult(BaseModel):
    """Structured result returned after grading a candidate's answer."""

    score: int = Field(ge=0, le=10)
    technical_accuracy: int = Field(ge=0, le=10)
    relevance: int = Field(ge=0, le=10)
    completeness: int = Field(ge=0, le=10)
    clarity: int = Field(ge=0, le=10)
    strengths: List[str] = Field(default_factory=list)
    weaknesses: List[str] = Field(default_factory=list)
    missing_concepts: List[str] = Field(default_factory=list)
    feedback: str = ""
    ideal_answer: str = ""
    follow_up_question: Optional[str] = None

    @field_validator(
        "score", "technical_accuracy", "relevance", "completeness", "clarity", mode="before"
    )
    @classmethod
    def _coerce_int(cls, v):
        try:
            return int(round(float(v)))
        except (TypeError, ValueError):
            return 0


class GeneratedQuestion(BaseModel):
    question: str
    category: str = "General"
    difficulty: str = "Medium"
    question_type: str = "Technical"


class AIProvider(ABC):
    """Every provider (OpenAI / Anthropic / Mock) implements this interface."""

    name: str = "base"

    @abstractmethod
    def generate_question(
        self,
        role: str,
        experience: str,
        technology: str,
        interview_type: str,
        difficulty: str,
        previous_questions: List[str],
        performance_hint: Optional[str] = None,
    ) -> GeneratedQuestion:
        raise NotImplementedError

    @abstractmethod
    def evaluate_answer(
        self,
        question: str,
        answer: str,
        role: str,
        experience: str,
        difficulty: str,
    ) -> EvaluationResult:
        raise NotImplementedError

    def is_live(self) -> bool:
        """True for real API-backed providers, False for the mock provider."""
        return self.name != "mock"
