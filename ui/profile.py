"""
Candidate profile page.
"""
import streamlit as st
from database import crud

EXPERIENCE_LEVELS = ["Fresher", "1-2 Years", "3-5 Years", "5+ Years"]
COMMON_ROLES = [
    "Python Developer",
    "Data Scientist",
    "Machine Learning Engineer",
    "AI Engineer",
    "Data Analyst",
    "Backend Developer",
    "Full Stack Developer",
    "Software Engineer",
    "Custom / Other",
]
TECHNOLOGIES = [
    "Python", "Java", "JavaScript", "SQL", "Machine Learning",
    "Data Science", "AI", "Web Development", "Other",
]


def render():
    st.title("👤 Candidate Profile")

    user = st.session_state.get("current_user")

    with st.form("profile_form"):
        name = st.text_input("Full Name", value=user["name"] if user else "")

        role_choice = st.selectbox(
            "Target Job Role",
            COMMON_ROLES,
            index=COMMON_ROLES.index(user["target_role"]) if user and user["target_role"] in COMMON_ROLES else 0,
        )
        custom_role = ""
        if role_choice == "Custom / Other":
            custom_role = st.text_input(
                "Enter custom role", value=user["target_role"] if user and user["target_role"] not in COMMON_ROLES else ""
            )

        experience = st.selectbox(
            "Experience Level",
            EXPERIENCE_LEVELS,
            index=EXPERIENCE_LEVELS.index(user["experience"]) if user and user["experience"] in EXPERIENCE_LEVELS else 0,
        )
        skills = st.text_area(
            "Skills (comma-separated)",
            value=user["skills"] if user else "",
            placeholder="e.g. Python, SQL, Pandas, REST APIs",
        )
        preferred_tech = st.selectbox(
            "Preferred Technology",
            TECHNOLOGIES,
            index=TECHNOLOGIES.index(user["preferred_technology"]) if user and user["preferred_technology"] in TECHNOLOGIES else 0,
        )

        submitted = st.form_submit_button("Save Profile", use_container_width=True)

    if submitted:
        final_role = custom_role.strip() if role_choice == "Custom / Other" else role_choice
        if not name.strip():
            st.error("Please enter your name.")
        elif not final_role:
            st.error("Please enter a target role.")
        else:
            saved = crud.create_or_update_user(
                name=name.strip(),
                target_role=final_role,
                experience=experience,
                skills=skills.strip(),
                preferred_technology=preferred_tech,
                user_id=user["id"] if user else None,
            )
            st.session_state["current_user"] = saved
            st.success("Profile saved successfully!")
            st.rerun()

    if user:
        st.divider()
        st.caption(f"Profile created: {user['created_at']}")
