"""
CRUD helper functions. All functions open their own session via
`get_session()` and return plain dicts (not ORM objects) so the
Streamlit UI layer never touches detached-session objects.
"""
import datetime
from typing import List, Optional, Dict, Any

from database.database import get_session
from database.models import User, Interview, Question, Answer, Performance
from utils.logger import log_error


def _user_to_dict(u: User) -> Dict[str, Any]:
    return {
        "id": u.id,
        "name": u.name,
        "target_role": u.target_role,
        "experience": u.experience,
        "skills": u.skills,
        "preferred_technology": u.preferred_technology,
        "created_at": u.created_at,
    }


def create_or_update_user(
    name: str,
    target_role: str,
    experience: str,
    skills: str,
    preferred_technology: str,
    user_id: Optional[int] = None,
) -> Dict[str, Any]:
    with get_session() as session:
        if user_id:
            user = session.get(User, user_id)
            if user is None:
                user = User()
                session.add(user)
        else:
            existing = session.query(User).filter(User.name == name).first()
            user = existing or User()
            if existing is None:
                session.add(user)

        user.name = name
        user.target_role = target_role
        user.experience = experience
        user.skills = skills
        user.preferred_technology = preferred_technology
        session.flush()
        return _user_to_dict(user)


def get_user(user_id: int) -> Optional[Dict[str, Any]]:
    with get_session() as session:
        user = session.get(User, user_id)
        return _user_to_dict(user) if user else None


def get_latest_user() -> Optional[Dict[str, Any]]:
    with get_session() as session:
        user = session.query(User).order_by(User.created_at.desc()).first()
        return _user_to_dict(user) if user else None


def create_interview(
    user_id: int, interview_type: str, technology: str, difficulty: str, total_questions: int
) -> int:
    with get_session() as session:
        interview = Interview(
            user_id=user_id,
            interview_type=interview_type,
            technology=technology,
            difficulty=difficulty,
            total_questions=total_questions,
            status="in_progress",
        )
        session.add(interview)
        session.flush()
        return interview.id


def add_question(
    interview_id: int, question: str, category: str, difficulty: str, question_type: str, order_number: int
) -> int:
    with get_session() as session:
        q = Question(
            interview_id=interview_id,
            question=question,
            category=category,
            difficulty=difficulty,
            question_type=question_type,
            order_number=order_number,
        )
        session.add(q)
        session.flush()
        return q.id


def save_answer(question_id: int, evaluation: dict, answer_text: str) -> int:
    with get_session() as session:
        a = Answer(
            question_id=question_id,
            answer=answer_text,
            score=evaluation.get("score", 0),
            technical_accuracy=evaluation.get("technical_accuracy", 0),
            relevance=evaluation.get("relevance", 0),
            completeness=evaluation.get("completeness", 0),
            clarity=evaluation.get("clarity", 0),
            feedback=evaluation.get("feedback", ""),
            strengths="|".join(evaluation.get("strengths", [])),
            weaknesses="|".join(evaluation.get("weaknesses", [])),
            missing_concepts="|".join(evaluation.get("missing_concepts", [])),
            ideal_answer=evaluation.get("ideal_answer", ""),
        )
        session.add(a)

        question = session.get(Question, question_id)
        if question is not None:
            perf = Performance(
                user_id=question.interview.user_id,
                interview_id=question.interview_id,
                topic=question.category,
                score=float(evaluation.get("score", 0)) * 10,
            )
            session.add(perf)

        session.flush()
        return a.id


def complete_interview(interview_id: int) -> None:
    with get_session() as session:
        interview = session.get(Interview, interview_id)
        if interview is None:
            return
        answers = (
            session.query(Answer)
            .join(Question, Answer.question_id == Question.id)
            .filter(Question.interview_id == interview_id)
            .all()
        )
        if answers:
            avg = sum(a.score for a in answers) / len(answers)
            interview.final_score = round(avg * 10, 1)  # store as percentage (0-100)
        interview.status = "completed"
        interview.completed_at = datetime.datetime.utcnow()


def abandon_interview(interview_id: int) -> None:
    with get_session() as session:
        interview = session.get(Interview, interview_id)
        if interview is not None and interview.status == "in_progress":
            interview.status = "abandoned"


def get_interview_detail(interview_id: int) -> Optional[Dict[str, Any]]:
    with get_session() as session:
        interview = session.get(Interview, interview_id)
        if interview is None:
            return None
        questions = []
        for q in sorted(interview.questions, key=lambda x: x.order_number):
            ans = q.answer
            questions.append(
                {
                    "id": q.id,
                    "question": q.question,
                    "category": q.category,
                    "difficulty": q.difficulty,
                    "question_type": q.question_type,
                    "order_number": q.order_number,
                    "answer": ans.answer if ans else None,
                    "score": ans.score if ans else None,
                    "technical_accuracy": ans.technical_accuracy if ans else None,
                    "relevance": ans.relevance if ans else None,
                    "completeness": ans.completeness if ans else None,
                    "clarity": ans.clarity if ans else None,
                    "feedback": ans.feedback if ans else "",
                    "strengths": ans.strengths.split("|") if ans and ans.strengths else [],
                    "weaknesses": ans.weaknesses.split("|") if ans and ans.weaknesses else [],
                    "missing_concepts": ans.missing_concepts.split("|")
                    if ans and ans.missing_concepts
                    else [],
                    "ideal_answer": ans.ideal_answer if ans else "",
                }
            )
        return {
            "id": interview.id,
            "user_id": interview.user_id,
            "interview_type": interview.interview_type,
            "technology": interview.technology,
            "difficulty": interview.difficulty,
            "total_questions": interview.total_questions,
            "final_score": interview.final_score,
            "started_at": interview.started_at,
            "completed_at": interview.completed_at,
            "status": interview.status,
            "candidate_name": interview.user.name if interview.user else "",
            "target_role": interview.user.target_role if interview.user else "",
            "questions": questions,
        }


def get_user_interviews(user_id: int) -> List[Dict[str, Any]]:
    with get_session() as session:
        interviews = (
            session.query(Interview)
            .filter(Interview.user_id == user_id)
            .order_by(Interview.started_at.desc())
            .all()
        )
        return [
            {
                "id": i.id,
                "interview_type": i.interview_type,
                "technology": i.technology,
                "difficulty": i.difficulty,
                "final_score": i.final_score,
                "started_at": i.started_at,
                "completed_at": i.completed_at,
                "status": i.status,
                "total_questions": i.total_questions,
            }
            for i in interviews
        ]


def get_dashboard_stats(user_id: int) -> Dict[str, Any]:
    with get_session() as session:
        interviews = (
            session.query(Interview)
            .filter(Interview.user_id == user_id, Interview.status == "completed")
            .all()
        )
        completed = len(interviews)
        avg_score = round(sum(i.final_score for i in interviews) / completed, 1) if completed else 0
        best_score = round(max((i.final_score for i in interviews), default=0), 1)

        questions_answered = (
            session.query(Answer)
            .join(Question, Answer.question_id == Question.id)
            .join(Interview, Question.interview_id == Interview.id)
            .filter(Interview.user_id == user_id)
            .count()
        )

        perf_records = session.query(Performance).filter(Performance.user_id == user_id).all()
        topic_scores: Dict[str, List[float]] = {}
        for p in perf_records:
            topic_scores.setdefault(p.topic, []).append(p.score)

        topic_avgs = {t: sum(s) / len(s) for t, s in topic_scores.items() if s}
        strongest = max(topic_avgs, key=topic_avgs.get) if topic_avgs else "N/A"
        weakest = min(topic_avgs, key=topic_avgs.get) if topic_avgs else "N/A"

        recent = (
            session.query(Interview)
            .filter(Interview.user_id == user_id)
            .order_by(Interview.started_at.desc())
            .limit(5)
            .all()
        )

        return {
            "interviews_completed": completed,
            "average_score": avg_score,
            "best_score": best_score,
            "questions_answered": questions_answered,
            "strongest_topic": strongest,
            "weakest_topic": weakest,
            "topic_averages": topic_avgs,
            "recent_interviews": [
                {
                    "id": i.id,
                    "type": i.interview_type,
                    "technology": i.technology,
                    "score": i.final_score,
                    "status": i.status,
                    "started_at": i.started_at,
                }
                for i in recent
            ],
            "score_trend": [
                {"date": i.completed_at or i.started_at, "score": i.final_score}
                for i in sorted(interviews, key=lambda x: x.started_at)
            ],
        }
