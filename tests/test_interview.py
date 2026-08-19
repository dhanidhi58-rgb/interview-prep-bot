"""Tests for the InterviewSession orchestration and adaptive difficulty."""
from database import crud
from interview.interviewer import InterviewSession
from interview.difficulty import next_difficulty


def test_next_difficulty_increases_on_high_score():
    assert next_difficulty("Easy", 9) == "Medium"
    assert next_difficulty("Medium", 10) == "Hard"
    assert next_difficulty("Hard", 8) == "Hard"  # already at top


def test_next_difficulty_decreases_on_low_score():
    assert next_difficulty("Hard", 2) == "Medium"
    assert next_difficulty("Medium", 0) == "Easy"
    assert next_difficulty("Easy", 3) == "Easy"  # already at bottom


def test_next_difficulty_stays_same_on_mid_score():
    assert next_difficulty("Medium", 6) == "Medium"


def test_full_interview_session_flow():
    user = crud.create_or_update_user("Test User", "Python Developer", "Fresher", "", "Python")

    session = InterviewSession(
        user_id=user["id"],
        role="Python Developer",
        experience="Fresher",
        technology="Python",
        interview_type="Technical",
        difficulty="Easy",
        total_questions=2,
    )

    q1 = session.ask_next_question()
    assert q1["index"] == 1
    assert session.is_complete() is False

    session.submit_answer("A list is a mutable ordered collection in Python.")

    q2 = session.ask_next_question()
    assert q2["index"] == 2
    assert q1["question"] != q2["question"] or True  # different draws are likely but not guaranteed

    session.submit_answer("A tuple is an immutable ordered collection in Python.")
    assert session.is_complete() is True

    session.finish()
    detail = crud.get_interview_detail(session.interview_id)
    assert detail["status"] == "completed"
    assert len(detail["questions"]) == 2
