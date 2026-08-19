"""
Coding Interview page: presents a problem, a code editor, runs
submitted code safely against test cases, and scores the result.
"""
import streamlit as st

from coding.problems import get_problem_by_difficulty, CODING_PROBLEMS
from coding.code_runner import run_candidate_code, docker_available
from coding.evaluator import score_submission


def render():
    st.title("💻 Coding Interview")

    if not docker_available():
        st.warning(
            "Docker was not detected on this machine. Code will run in a "
            "**restricted, best-effort demo sandbox** (separate process, "
            "5-second timeout, basic static screening) instead of a true "
            "isolated container. For safer execution, install Docker Desktop.",
            icon="⚠️",
        )
    else:
        st.success("Docker sandbox detected — code will run in an isolated, network-disabled container.", icon="🐳")

    if "coding_problem" not in st.session_state:
        default_difficulty = st.session_state.get("coding_setup", {}).get("difficulty", "Easy")
        st.session_state["coding_problem"] = get_problem_by_difficulty(default_difficulty)

    col_a, col_b = st.columns([3, 1])
    with col_b:
        if st.button("🔀 New Random Problem", use_container_width=True):
            st.session_state["coding_problem"] = get_problem_by_difficulty(
                st.session_state["coding_problem"]["difficulty"]
            )
            st.session_state.pop("code_submission", None)
            st.rerun()

        titles = [p["title"] for p in CODING_PROBLEMS]
        chosen = st.selectbox("Pick a specific problem", titles, index=titles.index(st.session_state["coding_problem"]["title"]))
        if chosen != st.session_state["coding_problem"]["title"]:
            st.session_state["coding_problem"] = next(p for p in CODING_PROBLEMS if p["title"] == chosen)
            st.session_state.pop("code_submission", None)
            st.rerun()

    problem = st.session_state["coding_problem"]

    with col_a:
        st.markdown(f"### {problem['title']} · *{problem['difficulty']}*")
        st.markdown(problem["statement"])
        st.markdown(f"**Constraints:** {problem['constraints']}")
        with st.expander("Examples"):
            for ex in problem["examples"]:
                st.code(f"Input: {ex['input']}\nOutput: {ex['output']}")

    st.divider()
    st.markdown(f"**Function signature:** `{problem['signature']}`")

    code = st.text_area(
        "Your Python solution",
        value=st.session_state.get("code_editor_value", problem["starter_code"]),
        height=280,
        key=f"code_editor_{problem['title']}",
    )

    if st.button("▶ Run & Submit", type="primary", use_container_width=True):
        with st.spinner("Running your code safely..."):
            run_result = run_candidate_code(code, problem["function_name"], problem["test_cases"])
            assessment = score_submission(run_result, code)
        st.session_state["code_submission"] = {"run_result": run_result, "assessment": assessment}

    submission = st.session_state.get("code_submission")
    if submission:
        _render_submission_result(submission, problem)


def _render_submission_result(submission, problem):
    run_result = submission["run_result"]
    assessment = submission["assessment"]

    st.divider()
    st.markdown("### Results")

    if run_result.get("stderr") and not run_result.get("results"):
        st.error("Your code raised an error before producing results:")
        st.code(run_result["stderr"])
        return

    col1, col2, col3 = st.columns(3)
    col1.metric("Score", f"{assessment['score']}/10")
    col2.metric("Tests Passed", f"{assessment['passed']}/{assessment['total']}")
    col3.metric("Correctness", f"{assessment['correctness_pct']}%")

    st.caption(f"Execution mode: **{run_result.get('mode')}**")

    if assessment["warnings"]:
        st.warning("Static screening flagged the following (informational only):\n\n" + "\n".join(f"- {w}" for w in assessment["warnings"]))

    st.markdown(f"**Estimated Time Complexity:** {assessment['complexity_note']}")
    st.markdown("**Code Quality Notes:**")
    for note in assessment["quality_notes"]:
        st.markdown(f"- {note}")

    st.markdown("#### Test Case Details")
    for i, r in enumerate(run_result.get("results", []), start=1):
        status = "✅ Passed" if r.get("passed") else "❌ Failed"
        with st.expander(f"Test {i}: {status}"):
            st.write(f"Input: `{r.get('input')}`")
            st.write(f"Expected: `{r.get('expected')}`")
            st.write(f"Your output: `{r.get('output')}`")
            if r.get("error"):
                st.error(r["error"])
