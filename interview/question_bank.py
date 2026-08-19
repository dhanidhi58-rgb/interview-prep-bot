"""
Loads the local question bank (data/question_bank.json) into memory.
Used by MockProvider and as a fallback source of questions for the
live providers if generation ever fails.
"""
import json
from pathlib import Path

_DATA_FILE = Path(__file__).resolve().parent.parent / "data" / "question_bank.json"

with open(_DATA_FILE, "r", encoding="utf-8") as _f:
    QUESTION_BANK = json.load(_f)

TECHNOLOGIES = [t for t in QUESTION_BANK.keys() if t != "HR"]
