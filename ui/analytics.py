"""
Performance Analytics page — deeper charts: score trend, topic
performance, per-question performance, and improvement comparison
between the two most recent interviews.
"""
import streamlit as st
import pandas as pd
import plotly.express as px

from database import crud


def render():
    st.title("📈 Performance Analytics")

    user = st.session_state.get("current_user")
    if not user:
        st.info("Create your candidate profile first from the **Profile** page.")
        return

    stats = crud.get_dashboard_stats(user["id"])
    interviews = crud.get_user_interviews(user["id"])
    completed = [i for i in interviews if i["status"] == "completed"]

    if not completed:
        st.info("Complete at least one interview to see analytics.")
        return

    st.markdown("### Score Trend Over Time")
    trend = stats["score_trend"]
    df_trend = pd.DataFrame(trend)
    fig = px.line(df_trend, x="date", y="score", markers=True)
    fig.update_layout(yaxis_range=[0, 100])
    st.plotly_chart(fig, use_container_width=True)

    st.markdown("### Topic-wise Performance")
    topic_avgs = stats["topic_averages"]
    if topic_avgs:
        df_topics = pd.DataFrame({"Topic": list(topic_avgs.keys()), "Score": list(topic_avgs.values())})
        fig2 = px.bar(df_topics.sort_values("Score"), x="Score", y="Topic", orientation="h", color="Score", color_continuous_scale="Blues")
        fig2.update_layout(xaxis_range=[0, 100])
        st.plotly_chart(fig2, use_container_width=True)

    st.markdown("### Question-by-Question Performance (Most Recent Interview)")
    latest = completed[0]
    detail = crud.get_interview_detail(latest["id"])
    q_rows = [
        {"Question": f"Q{i+1}", "Score": q["score"] or 0, "Category": q["category"]}
        for i, q in enumerate(detail["questions"])
    ]
    if q_rows:
        df_q = pd.DataFrame(q_rows)
        fig3 = px.bar(df_q, x="Question", y="Score", color="Category")
        fig3.update_layout(yaxis_range=[0, 10])
        st.plotly_chart(fig3, use_container_width=True)

    st.markdown("### Improvement: Last Interview vs Previous")
    if len(completed) >= 2:
        current, previous = completed[0], completed[1]
        delta = round((current["final_score"] or 0) - (previous["final_score"] or 0), 1)
        col1, col2 = st.columns(2)
        col1.metric("Previous Score", f"{previous['final_score']}%")
        col2.metric("Current Score", f"{current['final_score']}%", delta=f"{delta}%")
    else:
        st.info("Complete a second interview to see an improvement comparison.")
