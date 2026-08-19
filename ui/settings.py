"""
Settings page — shows current AI provider configuration (without
exposing full API keys), and lets the user tweak default interview
preferences for this session.
"""
import streamlit as st

from config.settings import settings

DIFFICULTIES = ["Easy", "Medium", "Hard", "Adaptive"]
QUESTION_COUNTS = [5, 10, 15, 20]


def render():
    st.title("⚙️ Settings")

    st.markdown("### AI Provider")
    effective = settings.effective_provider()
    requested = settings.AI_PROVIDER

    if effective == "mock":
        st.info(
            f"Running in **Demo Mode** (Mock AI Provider). "
            + (
                f"You requested `{requested}` but no valid API key was found, so the app "
                "automatically fell back to Demo Mode."
                if requested != "mock"
                else "Set `AI_PROVIDER` and an API key in your `.env` file to use a live AI provider."
            )
        )
    else:
        st.success(f"Running with live provider: **{effective}**")

    col1, col2 = st.columns(2)
    with col1:
        st.markdown("**OpenAI API Key**")
        st.code(settings.masked_key(settings.OPENAI_API_KEY))
    with col2:
        st.markdown("**Anthropic API Key**")
        st.code(settings.masked_key(settings.ANTHROPIC_API_KEY))

    st.caption(f"Model override (MODEL_NAME): `{settings.MODEL_NAME or '(provider default)'}`")

    st.divider()
    st.markdown("### Default Interview Preferences (this session)")
    default_difficulty = st.selectbox(
        "Default Difficulty",
        DIFFICULTIES,
        index=DIFFICULTIES.index(st.session_state.get("default_difficulty", "Medium")),
    )
    default_count = st.selectbox(
        "Default Question Count",
        QUESTION_COUNTS,
        index=QUESTION_COUNTS.index(st.session_state.get("default_question_count", 10)),
    )
    if st.button("Save Preferences"):
        st.session_state["default_difficulty"] = default_difficulty
        st.session_state["default_question_count"] = default_count
        st.success("Preferences saved for this session.")

    st.divider()
    st.markdown("### Database")
    st.code(settings.DATABASE_URL)

    st.divider()
    st.markdown("### How to Enable a Live AI Provider")
    st.markdown(
        "1. Copy `.env.example` to `.env`\n"
        "2. Set `AI_PROVIDER=openai` or `AI_PROVIDER=anthropic`\n"
        "3. Paste your API key into `OPENAI_API_KEY` or `ANTHROPIC_API_KEY`\n"
        "4. (Optional) Set `MODEL_NAME` to override the default model\n"
        "5. Restart the app: `streamlit run app.py`"
    )
