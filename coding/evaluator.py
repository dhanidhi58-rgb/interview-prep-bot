"""
Turns raw code_runner results into a scored coding-interview
assessment: correctness, an estimated complexity/quality note (via
simple heuristics, since real static analysis is out of scope), and
an overall score out of 10.
"""
from typing import Dict, Any


def score_submission(run_result: Dict[str, Any], candidate_code: str) -> Dict[str, Any]:
    total = run_result.get("total_count", 0)
    passed = run_result.get("passed_count", 0)
    correctness_pct = (passed / total * 100) if total else 0

    # Very simple heuristics for code quality signals (not real static analysis).
    lines = [l for l in candidate_code.splitlines() if l.strip()]
    has_comments = any(l.strip().startswith("#") for l in lines)
    has_docstring = '"""' in candidate_code or "'''" in candidate_code
    nested_loops = candidate_code.count("for ") + candidate_code.count("while ")

    if nested_loops >= 2:
        complexity_note = "Likely O(n^2) or worse — multiple loops detected. Consider whether a single pass or a hash map could help."
    elif nested_loops == 1:
        complexity_note = "Likely O(n) — a single loop was detected."
    else:
        complexity_note = "Likely O(1) or uses built-ins — no explicit loops detected."

    quality_notes = []
    if not has_comments and not has_docstring:
        quality_notes.append("No comments or docstring — consider documenting intent.")
    if len(lines) > 40:
        quality_notes.append("Solution is long — check if it can be simplified.")
    if not quality_notes:
        quality_notes.append("Code is reasonably concise.")

    score = round((correctness_pct / 100) * 10)

    return {
        "correctness_pct": round(correctness_pct, 1),
        "passed": passed,
        "total": total,
        "score": score,
        "complexity_note": complexity_note,
        "quality_notes": quality_notes,
        "warnings": run_result.get("warnings", []),
        "execution_mode": run_result.get("mode"),
    }
