"""
Reports page — generate and download a PDF report for any completed
interview.
"""
import streamlit as st

from database import crud
from reports.pdf_report import build_interview_report
from utils.logger import log_error


def render():
    st.title("📄 Reports")

    user = st.session_state.get("current_user")
    if not user:
        st.info("Create your candidate profile first from the **Profile** page.")
        return

    interviews = [i for i in crud.get_user_interviews(user["id"]) if i["status"] == "completed"]
    if not interviews:
        st.info("Complete an interview to generate a PDF report.")
        return

    options = {
        f"#{i['id']} · {i['started_at']:%Y-%m-%d %H:%M} · {i['interview_type']} · {i['technology']} · {i['final_score']}%": i["id"]
        for i in interviews
    }
    choice = st.selectbox("Select a completed interview", list(options.keys()))

    if choice and st.button("Generate PDF Report", type="primary"):
        detail = crud.get_interview_detail(options[choice])
        try:
            pdf_bytes = build_interview_report(detail)
            st.session_state["pdf_bytes"] = pdf_bytes
            st.session_state["pdf_filename"] = f"interview_report_{options[choice]}.pdf"
            st.success("Report generated.")
        except Exception as exc:
            log_error("ui.reports.generate", exc)
            st.error("Something went wrong generating the PDF report. Please try again.")

    if st.session_state.get("pdf_bytes"):
        st.download_button(
            "⬇ Download PDF Report",
            data=st.session_state["pdf_bytes"],
            file_name=st.session_state["pdf_filename"],
            mime="application/pdf",
            use_container_width=True,
        )
