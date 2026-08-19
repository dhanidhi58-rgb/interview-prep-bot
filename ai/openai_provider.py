"""
OpenAIProvider — talks to the OpenAI Chat Completions API and parses
its JSON output into our validated Pydantic models. Any failure
(network, malformed JSON, timeout, rate limit) is caught and raised
as a clean AIProviderError so the UI layer can show a friendly
message instead of a traceback.
"""
import json
from typing import List, Optional

from ai.base import AIProvider, EvaluationResult, GeneratedQuestion
from config.settings import settings
from utils.logger import log_error


class AIProviderError(Exception):
    """Raised whenever a live AI provider call fails for any reason."""


def _extract_json(text: str) -> dict:
    text = text.strip()
    if text.startswith("```"):
        text = text.strip("`")
        if text.lower().startswith("json"):
            text = text[4:]
    start = text.find("{")
    end = text.rfind("}")
    if start == -1 or end == -1:
        raise ValueError("No JSON object found in AI response")
    return json.loads(text[start : end + 1])


class OpenAIProvider(AIProvider):
    name = "openai"

    def __init__(self):
        try:
            from openai import OpenAI
        except ImportError as exc:
            raise AIProviderError(
                "The 'openai' package is not installed. Run: pip install openai"
            ) from exc

        if not settings.OPENAI_API_KEY:
            raise AIProviderError("OPENAI_API_KEY is not configured.")

        self._client = OpenAI(api_key=settings.OPENAI_API_KEY)
        self._model = settings.MODEL_NAME or "gpt-4o-mini"

    def _chat(self, system: str, user: str) -> dict:
        try:
            response = self._client.chat.completions.create(
                model=self._model,
                messages=[
                    {"role": "system", "content": system},
                    {"role": "user", "content": user},
                ],
                temperature=0.7,
                timeout=30,
            )
            content = response.choices[0].message.content or ""
            return _extract_json(content)
        except Exception as exc:  # network, auth, rate-limit, parsing, etc.
            log_error("OpenAIProvider._chat", exc)
            raise AIProviderError(f"OpenAI request failed: {exc}") from exc

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
            "question_type. No extra text."
        )
        user = (
            f"Role: {role}\nExperience: {experience}\nTechnology: {technology}\n"
            f"Interview type: {interview_type}\nDifficulty: {difficulty}\n"
            f"Previously asked questions (avoid repeating): {previous_questions}\n"
            f"Performance so far: {performance_hint or 'N/A'}\n"
            "Generate ONE new, relevant interview question."
        )
        data = self._chat(system, user)
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
            "follow_up_question (string or null). No extra text."
        )
        user = (
            f"Role: {role}\nExperience: {experience}\nDifficulty: {difficulty}\n"
            f"Question: {question}\nCandidate answer: {answer}\n"
            "Evaluate the answer now."
        )
        data = self._chat(system, user)
        return EvaluationResult(**data)
