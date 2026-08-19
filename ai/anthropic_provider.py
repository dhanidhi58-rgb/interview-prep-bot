"""
AnthropicProvider — talks to the Anthropic Messages API and parses
its JSON output into our validated Pydantic models. Mirrors
OpenAIProvider's error-handling behaviour.
"""
import json
from typing import List, Optional

from ai.base import AIProvider, EvaluationResult, GeneratedQuestion
from ai.openai_provider import AIProviderError, _extract_json
from config.settings import settings
from utils.logger import log_error


class AnthropicProvider(AIProvider):
    name = "anthropic"

    def __init__(self):
        try:
            import anthropic
        except ImportError as exc:
            raise AIProviderError(
                "The 'anthropic' package is not installed. Run: pip install anthropic"
            ) from exc

        if not settings.ANTHROPIC_API_KEY:
            raise AIProviderError("ANTHROPIC_API_KEY is not configured.")

        self._client = anthropic.Anthropic(api_key=settings.ANTHROPIC_API_KEY)
        self._model = settings.MODEL_NAME or "claude-sonnet-4-6"

    def _message(self, system: str, user: str) -> dict:
        try:
            response = self._client.messages.create(
                model=self._model,
                max_tokens=1000,
                system=system,
                messages=[{"role": "user", "content": user}],
            )
            text_parts = [b.text for b in response.content if getattr(b, "type", "") == "text"]
            content = "\n".join(text_parts)
            return _extract_json(content)
        except Exception as exc:
            log_error("AnthropicProvider._message", exc)
            raise AIProviderError(f"Anthropic request failed: {exc}") from exc

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
        system = (
            "You are a professional technical interviewer. Respond ONLY with a "
            "single JSON object with keys: question, category, difficulty, "
            "question_type. No extra text, no markdown fences."
        )
        user = (
            f"Role: {role}\nExperience: {experience}\nTechnology: {technology}\n"
            f"Interview type: {interview_type}\nDifficulty: {difficulty}\n"
            f"Previously asked questions (avoid repeating): {previous_questions}\n"
            f"Performance so far: {performance_hint or 'N/A'}\n"
            "Generate ONE new, relevant interview question."
        )
        data = self._message(system, user)
        return GeneratedQuestion(**data)

    def evaluate_answer(
        self,
        question: str,
        answer: str,
        role: str,
        experience: str,
        difficulty: str,
    ) -> EvaluationResult:
        system = (
            "You are a strict but fair technical interviewer grading a candidate's "
            "answer. Respond ONLY with a single JSON object with keys: score "
            "(0-10), technical_accuracy (0-10), relevance (0-10), completeness "
            "(0-10), clarity (0-10), strengths (list), weaknesses (list), "
            "missing_concepts (list), feedback (string), ideal_answer (string), "
            "follow_up_question (string or null). No extra text, no markdown fences."
        )
        user = (
            f"Role: {role}\nExperience: {experience}\nDifficulty: {difficulty}\n"
            f"Question: {question}\nCandidate answer: {answer}\n"
            "Evaluate the answer now."
        )
        data = self._message(system, user)
        return EvaluationResult(**data)
