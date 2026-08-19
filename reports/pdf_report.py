"""
Generates a professional PDF interview report using ReportLab.
Returns raw PDF bytes so the Streamlit UI can offer them directly
via st.download_button without touching the filesystem.
"""
import io
from datetime import datetime
from typing import Dict, Any

from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm
from reportlab.lib import colors
from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer,
    Table,
    TableStyle,
    PageBreak,
)

from utils.logger import log_error


def _styles():
    styles = getSampleStyleSheet()
    styles.add(
        ParagraphStyle(
            name="ReportTitle", fontSize=20, leading=24, spaceAfter=12, textColor=colors.HexColor("#1f2937")
        )
    )
    styles.add(
        ParagraphStyle(
            name="SectionHeading",
            fontSize=14,
            leading=18,
            spaceBefore=14,
            spaceAfter=8,
            textColor=colors.HexColor("#2563eb"),
        )
    )
    return styles


def _compute_topic_breakdown(questions):
    topic_scores: Dict[str, list] = {}
    for q in questions:
        if q.get("score") is not None:
            topic_scores.setdefault(q["category"], []).append(q["score"])
    return {t: sum(s) / len(s) for t, s in topic_scores.items() if s}


def build_interview_report(interview: Dict[str, Any]) -> bytes:
    """
    interview: dict as returned by database.crud.get_interview_detail()
    """
    try:
        buffer = io.BytesIO()
        doc = SimpleDocTemplate(
            buffer,
            pagesize=A4,
            topMargin=2 * cm,
            bottomMargin=2 * cm,
            leftMargin=2 * cm,
            rightMargin=2 * cm,
        )
        styles = _styles()
        story = []

        questions = interview.get("questions", [])
        answered = [q for q in questions if q.get("score") is not None]
        overall_score = interview.get("final_score") or (
            round(sum(q["score"] for q in answered) / len(answered) * 10, 1) if answered else 0
        )
        avg_technical = (
            round(sum(q.get("technical_accuracy") or 0 for q in answered) / len(answered) * 10, 1)
            if answered
            else 0
        )
        avg_clarity = (
            round(sum(q.get("clarity") or 0 for q in answered) / len(answered) * 10, 1)
            if answered
            else 0
        )

        topic_breakdown = _compute_topic_breakdown(questions)
        strong_topics = sorted(topic_breakdown, key=topic_breakdown.get, reverse=True)[:3]
        weak_topics = sorted(topic_breakdown, key=topic_breakdown.get)[:3]

        # --- Header ---
        story.append(Paragraph("AI Interview Preparation Report", styles["ReportTitle"]))
        story.append(
            Paragraph(
                f"Generated on {datetime.now().strftime('%d %B %Y, %H:%M')}", styles["Normal"]
            )
        )
        story.append(Spacer(1, 12))

        # --- Candidate info table ---
        info_data = [
            ["Candidate", interview.get("candidate_name", "N/A")],
            ["Target Role", interview.get("target_role", "N/A")],
            ["Interview Type", interview.get("interview_type", "N/A")],
            ["Technology", interview.get("technology", "N/A")],
            ["Difficulty", interview.get("difficulty", "N/A")],
            ["Total Questions", str(interview.get("total_questions", "N/A"))],
        ]
        info_table = Table(info_data, colWidths=[5 * cm, 10 * cm])
        info_table.setStyle(
            TableStyle(
                [
                    ("BACKGROUND", (0, 0), (0, -1), colors.HexColor("#eff6ff")),
                    ("TEXTCOLOR", (0, 0), (0, -1), colors.HexColor("#1e3a8a")),
                    ("FONTNAME", (0, 0), (0, -1), "Helvetica-Bold"),
                    ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#d1d5db")),
                    ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                    ("TOPPADDING", (0, 0), (-1, -1), 6),
                    ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
                ]
            )
        )
        story.append(info_table)
        story.append(Spacer(1, 16))

        # --- Score summary ---
        story.append(Paragraph("Overall Performance", styles["SectionHeading"]))
        score_data = [
            ["Overall Score", f"{overall_score}%"],
            ["Technical Accuracy (avg)", f"{avg_technical}%"],
            ["Communication / Clarity (avg)", f"{avg_clarity}%"],
        ]
        score_table = Table(score_data, colWidths=[7 * cm, 8 * cm])
        score_table.setStyle(
            TableStyle(
                [
                    ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#d1d5db")),
                    ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#dcfce7")),
                    ("TOPPADDING", (0, 0), (-1, -1), 6),
                    ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
                ]
            )
        )
        story.append(score_table)
        story.append(Spacer(1, 12))

        story.append(
            Paragraph(
                "Strong Topics: " + (", ".join(strong_topics) if strong_topics else "N/A"),
                styles["Normal"],
            )
        )
        story.append(
            Paragraph(
                "Topics to Improve: " + (", ".join(weak_topics) if weak_topics else "N/A"),
                styles["Normal"],
            )
        )
        story.append(Spacer(1, 12))

        # --- Recommendation ---
        story.append(Paragraph("Final Assessment", styles["SectionHeading"]))
        if overall_score >= 80:
            recommendation = (
                f"You appear interview-ready for {interview.get('target_role', 'this')} roles. "
                "Keep practicing to maintain this level of consistency."
            )
        elif overall_score >= 60:
            recommendation = (
                f"You are on a good track for {interview.get('target_role', 'this')} roles, but should "
                f"strengthen: {', '.join(weak_topics) if weak_topics else 'a few weaker topics'} before "
                "your real interview."
            )
        else:
            recommendation = (
                "More preparation is recommended before attempting real interviews for this role. "
                f"Focus especially on: {', '.join(weak_topics) if weak_topics else 'the fundamentals'}."
            )
        story.append(Paragraph(recommendation, styles["Normal"]))
        story.append(PageBreak())

        # --- Question by question ---
        story.append(Paragraph("Question-by-Question Breakdown", styles["SectionHeading"]))
        for i, q in enumerate(questions, start=1):
            story.append(Paragraph(f"Q{i}. {q['question']}", styles["Heading4"]))
            story.append(Paragraph(f"Category: {q.get('category', 'N/A')} | Difficulty: {q.get('difficulty', 'N/A')}", styles["Normal"]))
            if q.get("score") is not None:
                story.append(Paragraph(f"Score: {q['score']}/10", styles["Normal"]))
                story.append(Paragraph(f"Your answer: {q.get('answer') or '(no answer)'}", styles["Normal"]))
                story.append(Paragraph(f"Feedback: {q.get('feedback', '')}", styles["Normal"]))
                if q.get("strengths"):
                    story.append(Paragraph("Strengths: " + ", ".join(q["strengths"]), styles["Normal"]))
                if q.get("weaknesses"):
                    story.append(Paragraph("Weaknesses: " + ", ".join(q["weaknesses"]), styles["Normal"]))
                story.append(Paragraph(f"Ideal answer: {q.get('ideal_answer', '')}", styles["Normal"]))
            else:
                story.append(Paragraph("Not answered.", styles["Normal"]))
            story.append(Spacer(1, 10))

        doc.build(story)
        return buffer.getvalue()
    except Exception as exc:
        log_error("build_interview_report", exc)
        raise
