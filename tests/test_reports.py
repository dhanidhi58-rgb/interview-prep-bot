"""Tests for PDF report generation."""
from database import crud
from reports.pdf_report import build_interview_report


def _completed_interview_detail():
    user = crud.create_or_update_user("Report Test", "Python Developer", "Fresher", "", "Python")
    interview_id = crud.create_interview(user["id"], "Technical", "Python", "Easy", 1)
    q_id = crud.add_question(interview_id, "What is a list?", "Data Types", "Easy", "Technical", 1)
    evaluation = {
        "score": 9,
        "technical_accuracy": 9,
        "relevance": 9,
        "completeness": 8,
        "clarity": 9,
        "strengths": ["Clear explanation"],
        "weaknesses": [],
        "missing_concepts": [],
        "feedback": "Excellent answer.",
        "ideal_answer": "A list is a mutable ordered collection.",
    }
    crud.save_answer(q_id, evaluation, "A list is a mutable ordered collection of items.")
    crud.complete_interview(interview_id)
    return crud.get_interview_detail(interview_id)


def test_pdf_report_generates_nonempty_bytes():
    detail = _completed_interview_detail()
    pdf_bytes = build_interview_report(detail)
    assert isinstance(pdf_bytes, bytes)
    assert len(pdf_bytes) > 500
    assert pdf_bytes[:4] == b"%PDF"
