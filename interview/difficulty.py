"""
Adaptive difficulty logic.

Score 8-10 -> increase difficulty
Score 5-7  -> maintain difficulty
Score 0-4  -> decrease difficulty
"""
_LADDER = ["Easy", "Medium", "Hard"]


def next_difficulty(current: str, last_score: int) -> str:
    if current not in _LADDER:
        current = "Medium"

    idx = _LADDER.index(current)

    if last_score >= 8:
        idx = min(idx + 1, len(_LADDER) - 1)
    elif last_score <= 4:
        idx = max(idx - 1, 0)
    # 5-7 -> stay the same

    return _LADDER[idx]
