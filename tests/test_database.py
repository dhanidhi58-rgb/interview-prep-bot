"""Tests for database initialization, users, and interviews."""
from database import crud
from database.database import get_session
from database.models import User


def test_database_initializes_and_is_empty():
    with get_session() as session:
        assert session.query(User).count() == 0


def test_create_user():
    user = crud.create_or_update_user(
        name="Jane Doe",
        target_role="Python Developer",
        experience="1-2 Years",
        skills="Python, SQL",
        preferred_technology="Python",
    )
    assert user["id"] is not None
    assert user["name"] == "Jane Doe"

    fetched = crud.get_user(user["id"])
    assert fetched["target_role"] == "Python Developer"


def test_update_existing_user():
    user = crud.create_or_update_user(
        name="Jane Doe",
        target_role="Python Developer",
        experience="1-2 Years",
        skills="Python",
        preferred_technology="Python",
    )
    updated = crud.create_or_update_user(
        name="Jane Doe",
        target_role="Backend Developer",
        experience="3-5 Years",
        skills="Python, Docker",
        preferred_technology="Python",
        user_id=user["id"],
    )
    assert updated["id"] == user["id"]
    assert updated["target_role"] == "Backend Developer"


def test_create_interview_and_questions():
    user = crud.create_or_update_user("Sam", "Data Scientist", "Fresher", "", "Python")
    interview_id = crud.create_interview(user["id"], "Technical", "Python", "Easy", 5)
    assert interview_id is not None

    q_id = crud.add_question(interview_id, "What is a list?", "Data Types", "Easy", "Technical", 1)
    assert q_id is not None

    detail = crud.get_interview_detail(interview_id)
    assert detail["status"] == "in_progress"
    assert len(detail["questions"]) == 1


def test_complete_interview_calculates_score():
    user = crud.create_or_update_user("Alex", "AI Engineer", "Fresher", "", "Python")
    interview_id = crud.create_interview(user["id"], "Technical", "Python", "Easy", 1)
    q_id = crud.add_question(interview_id, "What is a list?", "Data Types", "Easy", "Technical", 1)

    evaluation = {
        "score": 8,
        "technical_accuracy": 8,
        "relevance": 8,
        "completeness": 8,
        "clarity": 8,
        "strengths": ["Clear"],
        "weaknesses": [],
        "missing_concepts": [],
        "feedback": "Good job",
        "ideal_answer": "A list is...",
    }
    crud.save_answer(q_id, evaluation, "A list is a mutable ordered collection.")
    crud.complete_interview(interview_id)

    detail = crud.get_interview_detail(interview_id)
    assert detail["status"] == "completed"
    assert detail["final_score"] == 80.0


def test_dashboard_stats_with_no_data():
    user = crud.create_or_update_user("NoData", "QA Engineer", "Fresher", "", "Python")
    stats = crud.get_dashboard_stats(user["id"])
    assert stats["interviews_completed"] == 0
    assert stats["average_score"] == 0
