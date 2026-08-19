"""
Dashboard page — key metrics, recent interviews, and performance
charts for the active candidate.
"""
import streamlit as st
import pandas as pd
import plotly.express as px

from database import crud


def render():
    st.title("📊 Dashboard")

    user = st.session_state.get("current_user")
    if not user:
        st.info("Create your candidate profile first from the **Profile** page.")
        return

    stats = crud.get_dashboard_stats(user["id"])

    st.subheader(f"Welcome back, {user['name']} 👋")
    st.caption(f"Target role: **{user['target_role']}** · Experience: **{user['experience']}**")

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Interviews Completed", stats["interviews_completed"])
    col2.metric("Average Score", f"{stats['average_score']}%")
    col3.metric("Best Score", f"{stats['best_score']}%")
    col4.metric("Questions Answered", stats["questions_answered"])

    col5, col6 = st.columns(2)
    col5.metric("Strongest Topic", stats["strongest_topic"])
    col6.metric("Weakest Topic", stats["weakest_topic"])

    st.divider()

    chart_col1, chart_col2 = st.columns(2)

    with chart_col1:
        st.markdown("#### Score Trend")
        trend = stats["score_trend"]
        if trend:
            df = pd.DataFrame(trend)
            fig = px.line(df, x="date", y="score", markers=True)
            fig.update_layout(yaxis_range=[0, 100], height=350)
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("Complete an interview to see your score trend.")

    with chart_col2:
        st.markdown("#### Topic-wise Performance")
        topic_avgs = stats["topic_averages"]
        if topic_avgs:
            df = pd.DataFrame(
                {"topic": list(topic_avgs.keys()), "score": list(topic_avgs.values())}
            )
            fig = px.bar(df, x="topic", y="score", color="score", color_continuous_scale="Blues")
            fig.update_layout(yaxis_range=[0, 100], height=350)
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("Complete an interview to see topic-wise performance.")

    st.divider()
    st.markdown("#### Recent Interviews")
    recent = stats["recent_interviews"]
    if recent:
        df = pd.DataFrame(recent)
        df = df.rename(
            columns={
                "type": "Type",
                "technology": "Technology",
                "score": "Score",
                "status": "Status",
                "started_at": "Started",
            }
        )
        st.dataframe(df[["Started", "Type", "Technology", "Score", "Status"]], use_container_width=True, hide_index=True)
    else:
        st.info("No interviews yet. Start one from **Start Interview**.")
