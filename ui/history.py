"""
Interview History page — list of past interviews with drill-down
into each one's full question/answer/feedback record.
"""
import streamlit as st
import pandas as pd

from database import crud


def render():
    st.title("🗂️ Interview History")

    user = st.session_state.get("current_user")
    if not user:
        st.info("Create your candidate profile first from the **Profile** page.")
        return

    interviews = crud.get_user_interviews(user["id"])
    if not interviews:
        st.info("No interviews yet. Start one from **Start Interview**.")
        return

    df = pd.DataFrame(interviews)
    display_df = df.rename(
        columns={
            "started_at": "Date",
            "target_role": "Role",
            "interview_type": "Type",
            "technology": "Technology",
            "final_score": "Score",
            "status": "Status",
        }
    )
    display_df["Role"] = user["target_role"]

    st.dataframe(
        display_df[["Date", "Role", "Type", "Technology", "Score", "Status"]],
        use_container_width=True,
        hide_index=True,
    )

    st.divider()
    st.markdown("### View a Past Interview")
    options = {
        f"#{i['id']} · {i['started_at']:%Y-%m-%d %H:%M} · {i['interview_type']} · {i['technology']} · {i['status']}": i["id"]
        for i in interviews
    }
    choice = st.selectbox("Select interview", list(options.keys()))
    if choice:
        detail = crud.get_interview_detail(options[choice])
        _render_detail(detail)


def _render_detail(detail):
    if not detail:
        st.error("Interview not found.")
        return

    st.markdown(f"#### Interview #{detail['id']} — {detail['interview_type']} / {detail['technology']}")
    col1, col2, col3 = st.columns(3)
    col1.metric("Final Score", f"{detail['final_score'] or 0}%")
    col2.metric("Status", detail["status"])
    col3.metric("Questions", detail["total_questions"])

    for i, q in enumerate(detail["questions"], start=1):
        with st.expander(f"Q{i}. {q['question']} — Score: {q['score'] if q['score'] is not None else 'N/A'}"):
            st.markdown(f"**Category:** {q['category']} · **Difficulty:** {q['difficulty']}")
            st.markdown(f"**Your answer:** {q['answer'] or '_(no answer)_'}")
            if q["score"] is not None:
                st.markdown(f"**Feedback:** {q['feedback']}")
                if q["strengths"]:
                    st.markdown("**Strengths:** " + ", ".join(q["strengths"]))
                if q["weaknesses"]:
                    st.markdown("**Weaknesses:** " + ", ".join(q["weaknesses"]))
                st.markdown(f"**Ideal answer:** {q['ideal_answer']}")
