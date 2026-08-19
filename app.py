"""
AI Interview Preparation Bot — main Streamlit entry point.

Run with:
    streamlit run app.py
"""
import streamlit as st

from database.database import init_db
from database import crud
from config.settings import settings
from utils.logger import log_error

from ui import dashboard, profile, interview, coding, history, analytics, reports, settings as settings_page

st.set_page_config(
    page_title="AI Interview Prep Bot",
    page_icon="🎯",
    layout="wide",
    initial_sidebar_state="expanded",
)

# --- One-time initialization ---
if "db_initialized" not in st.session_state:
    try:
        init_db()
        st.session_state["db_initialized"] = True
    except Exception as exc:
        log_error("init_db", exc)
        st.error("Could not initialize the database. Check logs/app.log for details.")
        st.stop()

if "current_user" not in st.session_state:
    try:
        st.session_state["current_user"] = crud.get_latest_user()
    except Exception as exc:
        log_error("load_latest_user", exc)
        st.session_state["current_user"] = None

PAGES = {
    "Dashboard": dashboard.render,
    "Profile": profile.render,
    "Start Interview": interview.render_setup,
    "Live Interview": interview.render_live,
    "Coding Interview": coding.render,
    "History": history.render,
    "Analytics": analytics.render,
    "Reports": reports.render,
    "Settings": settings_page.render,
}

with st.sidebar:
    st.markdown("## 🎯 Interview Prep Bot")
    provider = settings.effective_provider()
    badge = "🧪 Demo Mode" if provider == "mock" else f"🤖 {provider.title()} (Live)"
    st.caption(badge)

    user = st.session_state.get("current_user")
    if user:
        st.markdown(f"**{user['name']}**")
        st.caption(user["target_role"])
    else:
        st.caption("No profile yet — go to Profile.")

    st.divider()

    default_page = st.session_state.pop("nav_override", None) or "Dashboard"
    page_names = list(PAGES.keys())
    default_index = page_names.index(default_page) if default_page in page_names else 0

    selected_page = st.radio("Navigate", page_names, index=default_index, label_visibility="collapsed")

try:
    PAGES[selected_page]()
except Exception as exc:
    log_error(f"render_page:{selected_page}", exc)
    st.error(
        "Something went wrong loading this page. The technical details have been "
        "logged. Please try again or navigate to a different page."
    )
