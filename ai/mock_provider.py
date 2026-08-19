"""
MockProvider — makes the entire application fully usable with
ZERO API keys. It deterministically generates plausible interview
questions and evaluations by pulling from the local question bank
and using simple heuristics to "score" answers.

This is what powers Demo Mode.
"""
import random
from typing import List, Optional

from ai.base import AIProvider, EvaluationResult, GeneratedQuestion
from interview.question_bank import QUESTION_BANK

_FILLER_STRENGTHS = [
    "Clear structure in the explanation",
    "Correct use of core terminology",
    "Good real-world example",
    "Logical step-by-step reasoning",
]
_FILLER_WEAKNESSES = [
    "Could go deeper into edge cases",
    "Missed mentioning time/space complexity",
    "Explanation could be more concise",
    "Did not compare with alternative approaches",
]


class MockProvider(AIProvider):
    name = "mock"

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
        pool = QUESTION_BANK.get(technology, QUESTION_BANK.get("Python", []))
        if interview_type in ("HR", "Behavioral"):
            pool = QUESTION_BANK.get("HR", pool)

        difficulty_pool = [q for q in pool if q["difficulty"] == difficulty] or pool
        unused = [q for q in difficulty_pool if q["question"] not in previous_questions]
        candidates = unused or difficulty_pool or pool

        if not candidates:
            return GeneratedQuestion(
                question=f"Tell me about a challenging {technology} problem you solved recently.",
                category=technology,
                difficulty=difficulty,
                question_type=interview_type,
            )

        chosen = random.choice(candidates)
        return GeneratedQuestion(
            question=chosen["question"],
            category=chosen.get("category", technology),
            difficulty=chosen.get("difficulty", difficulty),
            question_type=interview_type,
        )

    def evaluate_answer(
        self,
        question: str,
        answer: str,
        role: str,
        experience: str,
        difficulty: str,
    ) -> EvaluationResult:
        answer = (answer or "").strip()

        if not answer:
            return EvaluationResult(
                score=0,
                technical_accuracy=0,
                relevance=0,
                completeness=0,
                clarity=0,
                strengths=[],
                weaknesses=["No answer was provided"],
                missing_concepts=["A complete response is required"],
                feedback="You did not provide an answer. Try to always attempt a response, "
                "even a partial one, since interviewers value structured thinking over silence.",
                ideal_answer="A strong answer would define the concept, explain how it "
                "works, and give a concrete example relevant to the question.",
                follow_up_question=None,
            )

        word_count = len(answer.split())
        length_score = min(4, word_count / 25)
        keyword_bonus = 1 if any(
            kw in answer.lower()
            for kw in ["because", "example", "for instance", "which means", "in other words"]
        ) else 0
        random.seed(hash(question + answer) % (2**32))
        variability = random.uniform(-0.5, 1.5)

        base = 3 + length_score + keyword_bonus + variability
        score = max(0, min(10, round(base)))

        technical_accuracy = max(0, min(10, score + random.choice([-1, 0, 0, 1])))
        relevance = max(0, min(10, score + random.choice([-1, 0, 1])))
        completeness = max(0, min(10, score + random.choice([-2, -1, 0])))
        clarity = max(0, min(10, score + random.choice([-1, 0, 1])))

        strengths = random.sample(_FILLER_STRENGTHS, k=2 if score >= 5 else 1)
        weaknesses = random.sample(_FILLER_WEAKNESSES, k=1 if score >= 7 else 2)

        if score >= 8:
            feedback = "Strong answer — well structured, technically sound, and clearly communicated."
        elif score >= 5:
            feedback = "Solid attempt. The core idea is there, but the answer could be more complete."
        else:
            feedback = "The answer needs more depth and technical accuracy. Review the core concept again."

        follow_up = None
        if score >= 8:
            follow_up = f"Can you explain a scenario where this approach in '{question[:40]}...' might fail?"

        return EvaluationResult(
            score=score,
            technical_accuracy=technical_accuracy,
            relevance=relevance,
            completeness=completeness,
            clarity=clarity,
            strengths=strengths,
            weaknesses=weaknesses,
            missing_concepts=[] if score >= 8 else ["Deeper edge-case discussion"],
            feedback=feedback,
            ideal_answer=f"A strong answer to '{question}' would clearly define the concept, "
            "walk through how it works step by step, mention trade-offs, and finish "
            "with a concrete, relevant example.",
            follow_up_question=follow_up,
        )
