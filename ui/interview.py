"""
Start Interview + Live Interview + Result pages.

Interview state lives entirely in st.session_state so it survives
Streamlit reruns (every widget interaction triggers a rerun).
"""
import streamlit as st

from interview.interviewer import InterviewSession
from interview.question_bank import TECHNOLOGIES
from database import crud

INTERVIEW_TYPES = ["Technical", "HR", "Behavioral", "Coding", "Mixed"]
DIFFICULTIES = ["Easy", "Medium", "Hard", "Adaptive"]
QUESTION_COUNTS = [5, 10, 15, 20]


def _reset_interview_state():
    for key in ["interview_session", "current_q", "interview_finished", "last_eval"]:
        st.session_state.pop(key, None)


def render_setup():
    st.title("🎯 Start Interview")

    user = st.session_state.get("current_user")
    if not user:
        st.info("Please create your candidate profile first from the **Profile** page.")
        return

    st.caption(f"Candidate: **{user['name']}** · Role: **{user['target_role']}**")

    with st.form("setup_form"):
        col1, col2 = st.columns(2)
        interview_type = col1.selectbox("Interview Type", INTERVIEW_TYPES)
        technology = col2.selectbox(
            "Technology",
            TECHNOLOGIES,
            index=TECHNOLOGIES.index(user["preferred_technology"]) if user["preferred_technology"] in TECHNOLOGIES else 0,
        )

        col3, col4 = st.columns(2)
        difficulty = col3.selectbox("Difficulty", DIFFICULTIES)
        num_questions = col4.selectbox("Number of Questions", QUESTION_COUNTS)

        start = st.form_submit_button("🚀 START INTERVIEW", use_container_width=True)

    if start:
        if interview_type == "Coding":
            st.session_state["coding_setup"] = {
                "difficulty": "Medium" if difficulty == "Adaptive" else difficulty,
            }
            st.session_state["nav_override"] = "Coding Interview"
            st.rerun()
            return

        effective_difficulty = "Medium" if difficulty == "Adaptive" else difficulty
        _reset_interview_state()
        session = InterviewSession(
            user_id=user["id"],
            role=user["target_role"],
            experience=user["experience"],
            technology=technology,
            interview_type=interview_type,
            difficulty=effective_difficulty,
            total_questions=num_questions,
        )
        st.session_state["interview_session"] = session
        st.session_state["current_q"] = session.ask_next_question()
        st.session_state["interview_finished"] = False
        st.session_state["nav_override"] = "Live Interview"
        st.rerun()


def render_live():
    st.title("🎤 Live Interview")

    session: InterviewSession = st.session_state.get("interview_session")
    if not session:
        st.info("No interview in progress. Start one from **Start Interview**.")
        return

    if st.session_state.get("interview_finished"):
        _render_result(session)
        return

    provider_label = "🧪 Demo Mode (Mock AI)" if session.provider_name == "mock" else f"🤖 Live AI ({session.provider_name})"
    st.caption(provider_label)

    progress = min(session.question_index / session.total_questions, 1.0)
    st.progress(progress, text=f"Question {session.question_index} of {session.total_questions}")

    q = st.session_state["current_q"]

    with st.container(border=True):
        st.markdown(f"**Category:** {q['category']} · **Difficulty:** {q['difficulty']} · **Type:** {q['question_type']}")
        st.markdown(f"### {q['question']}")

        answer_key = f"answer_{q['id']}"
        answer = st.text_area("Your answer", key=answer_key, height=180, placeholder="Type your answer here...")

        col1, col2 = st.columns([1, 1])
        submit = col1.button("Submit Answer", type="primary", use_container_width=True)
        skip = col2.button("Skip Question", use_container_width=True)

    if submit or skip:
        answer_text = "" if skip else answer
        result = session.submit_answer(answer_text)
        st.session_state["last_eval"] = result
        st.session_state["show_feedback"] = True
        st.rerun()

    if st.session_state.get("show_feedback"):
        _render_feedback(st.session_state["last_eval"])
        if st.button("Next Question ➜", type="primary", use_container_width=True):
            st.session_state["show_feedback"] = False
            if session.is_complete():
                session.finish()
                st.session_state["interview_finished"] = True
            else:
                st.session_state["current_q"] = session.ask_next_question()
            st.rerun()


def _render_feedback(result: dict):
    st.divider()
    score = result["score"]
    color = "🟢" if score >= 8 else ("🟡" if score >= 5 else "🔴")
    st.markdown(f"### {color} Score: {score}/10")

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Technical Accuracy", f"{result['technical_accuracy']}/10")
    col2.metric("Relevance", f"{result['relevance']}/10")
    col3.metric("Completeness", f"{result['completeness']}/10")
    col4.metric("Clarity", f"{result['clarity']}/10")

    st.markdown(f"**Feedback:** {result['feedback']}")

    if result["strengths"]:
        st.markdown("**Strengths:**")
        for s in result["strengths"]:
            st.markdown(f"- ✅ {s}")
    if result["weaknesses"]:
        st.markdown("**Weaknesses:**")
        for w in result["weaknesses"]:
            st.markdown(f"- ⚠️ {w}")
    if result.get("missing_concepts"):
        st.markdown("**Missing Concepts:**")
        for m in result["missing_concepts"]:
            st.markdown(f"- 🔎 {m}")

    with st.expander("💡 Ideal Answer"):
        st.write(result["ideal_answer"])

    if result.get("follow_up_question"):
        st.info(f"Follow-up to consider: {result['follow_up_question']}")


def _render_result(session: InterviewSession):
    detail = crud.get_interview_detail(session.interview_id)
    if not detail:
        st.error("Could not load interview results.")
        return

    st.balloons()
    st.markdown("## 🏁 INTERVIEW COMPLETED")

    overall = detail["final_score"] or 0
    answered = [q for q in detail["questions"] if q.get("score") is not None]
    technical = round(sum(q.get("technical_accuracy") or 0 for q in answered) / len(answered) * 10, 1) if answered else 0
    clarity = round(sum(q.get("clarity") or 0 for q in answered) / len(answered) * 10, 1) if answered else 0

    col1, col2, col3 = st.columns(3)
    col1.metric("Overall Score", f"{overall}/100")
    col2.metric("Technical Skills", f"{technical}%")
    col3.metric("Communication", f"{clarity}%")

    topic_scores = {}
    for q in answered:
        topic_scores.setdefault(q["category"], []).append(q["score"])
    topic_avgs = {t: sum(s) / len(s) for t, s in topic_scores.items()}
    strong = sorted(topic_avgs, key=topic_avgs.get, reverse=True)[:3]
    weak = sorted(topic_avgs, key=topic_avgs.get)[:3]

    col4, col5 = st.columns(2)
    with col4:
        st.markdown("**Strong Areas**")
        for t in strong:
            st.markdown(f"✓ {t}")
    with col5:
        st.markdown("**Needs Improvement**")
        for t in weak:
            st.markdown(f"⚠ {t}")

    if overall >= 80:
        rec = f"You are interview-ready for {detail['target_role']} roles."
    elif overall >= 60:
        rec = f"You're close to interview-ready for {detail['target_role']} roles, but should improve: {', '.join(weak) if weak else 'a few weak areas'}."
    else:
        rec = f"More preparation is recommended before real interviews for {detail['target_role']} roles. Focus on: {', '.join(weak) if weak else 'the fundamentals'}."

    st.markdown("### Recommendation")
    st.info(rec)

    st.divider()
    if st.button("Start a New Interview", use_container_width=True):
        _reset_interview_state()
        st.session_state["nav_override"] = "Start Interview"
        st.rerun()

    st.caption("Full question-by-question review is available in **History**, and you can download a PDF report from **Reports**.")
