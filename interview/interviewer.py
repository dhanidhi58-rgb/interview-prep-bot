"""
High-level orchestration for a live interview session:
question -> answer -> evaluate -> adapt difficulty -> next question.

This class is UI-agnostic; ui/interview.py drives it from Streamlit
session state so progress survives Streamlit reruns.
"""
from typing import List, Optional, Dict, Any

from ai.factory import get_ai_provider
from interview.question_generator import QuestionGenerator
from interview.evaluator import Evaluator
from interview.difficulty import next_difficulty
from database import crud


class InterviewSession:
    def __init__(
        self,
        user_id: int,
        role: str,
        experience: str,
        technology: str,
        interview_type: str,
        difficulty: str,
        total_questions: int,
    ):
        self.user_id = user_id
        self.role = role
        self.experience = experience
        self.technology = technology
        self.interview_type = interview_type
        self.difficulty = difficulty
        self.total_questions = total_questions

        provider = get_ai_provider()
        self.provider_name = provider.name
        self.generator = QuestionGenerator(provider)
        self.evaluator = Evaluator(provider)

        self.interview_id = crud.create_interview(
            user_id, interview_type, technology, difficulty, total_questions
        )

        self.asked_questions: List[str] = []
        self.current_question_id: Optional[int] = None
        self.current_question_text: Optional[str] = None
        self.question_index = 0
        self.scores: List[int] = []

    def ask_next_question(self) -> Dict[str, Any]:
        performance_hint = (
            f"Average score so far: {sum(self.scores)/len(self.scores):.1f}/10"
            if self.scores
            else None
        )
        gq = self.generator.next_question(
            role=self.role,
            experience=self.experience,
            technology=self.technology,
            interview_type=self.interview_type,
            difficulty=self.difficulty,
            previous_questions=self.asked_questions,
            performance_hint=performance_hint,
        )
        self.question_index += 1
        q_id = crud.add_question(
            interview_id=self.interview_id,
            question=gq.question,
            category=gq.category,
            difficulty=gq.difficulty,
            question_type=gq.question_type,
            order_number=self.question_index,
        )
        self.asked_questions.append(gq.question)
        self.current_question_id = q_id
        self.current_question_text = gq.question

        return {
            "id": q_id,
            "question": gq.question,
            "category": gq.category,
            "difficulty": gq.difficulty,
            "question_type": gq.question_type,
            "index": self.question_index,
        }

    def submit_answer(self, answer_text: str) -> Dict[str, Any]:
        result = self.evaluator.evaluate(
            question=self.current_question_text,
            answer=answer_text,
            role=self.role,
            experience=self.experience,
            difficulty=self.difficulty,
        )
        crud.save_answer(self.current_question_id, result.model_dump(), answer_text)
        self.scores.append(result.score)

        if self.difficulty != "Adaptive-locked":
            self.difficulty = next_difficulty(self.difficulty, result.score)

        return result.model_dump()

    def is_complete(self) -> bool:
        return self.question_index >= self.total_questions

    def finish(self) -> None:
        crud.complete_interview(self.interview_id)
