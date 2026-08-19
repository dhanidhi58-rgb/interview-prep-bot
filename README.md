# 🎯 AI Interview Preparation Bot

A full-featured, locally-run AI interview coach built with **Python + Streamlit**. It simulates a real technical/HR interviewer, evaluates your answers, adapts difficulty as you go, tracks your progress over time, and generates downloadable PDF reports.

**Works immediately with zero API keys** via a built-in Demo Mode, and upgrades seamlessly to real AI (OpenAI or Anthropic) once you add a key.

---

## 1. Features

- **Dashboard** — interviews completed, average/best score, strongest/weakest topic, score trend and topic charts
- **Candidate Profile** — name, target role, experience level, skills, preferred technology
- **Interview Setup** — Technical / HR / Behavioral / Coding / Mixed, any technology, Easy/Medium/Hard/Adaptive difficulty, 5–20 questions
- **Live AI Interviewer** — asks one question at a time, evaluates your answer (technical accuracy, relevance, completeness, clarity), shows strengths/weaknesses/missing concepts, and reveals the ideal answer only after you submit
- **Adaptive Difficulty** — score 8–10 raises difficulty, 5–7 holds steady, 0–4 lowers it
- **Coding Interview Mode** — a Python code editor, safe test-case execution (Docker-sandboxed when available, restricted-subprocess demo mode otherwise), pass/fail results, and a rough complexity/quality assessment
- **Interview History** — every past interview, fully drillable question-by-question
- **Performance Analytics** — score trend, topic breakdown, per-question chart, interview-over-interview improvement
- **PDF Reports** — a professional report per completed interview, downloadable from the app
- **Settings** — see which AI provider is active (without exposing full API keys), tweak session defaults
- **Demo Mode** — a local Mock AI provider means the whole app works with **no API key at all**
- **Robust error handling** — friendly messages everywhere; technical details go to `logs/app.log`, never to the screen

---

## 2. Architecture

```text
Streamlit UI (ui/*.py)
        │
        ▼
Interview Orchestration (interview/interviewer.py)
        │
        ├──► Question Generator ──┐
        ├──► Evaluator ───────────┤
        │                         ▼
        │                 AIProvider (ai/base.py)
        │                         │
        │        ┌────────────────┼────────────────┐
        │        ▼                ▼                 ▼
        │   OpenAIProvider  AnthropicProvider   MockProvider
        │   (needs key)     (needs key)        (no key needed)
        ▼
Database (SQLAlchemy + SQLite) — users, interviews, questions, answers, performance
        │
        ▼
Reports (ReportLab PDF) · Analytics (Plotly charts)
```

The `AIProvider` abstraction means the rest of the app never talks to OpenAI/Anthropic directly — it only calls `generate_question()` / `evaluate_answer()`. `ai/factory.py` decides which concrete provider to use, and **automatically falls back to `MockProvider` any time a live provider is unconfigured or fails**, so the app can never get "stuck."

---

## 3. Tech Stack

Python 3.11+, Streamlit, SQLite, SQLAlchemy, Pandas, Plotly, Pydantic, python-dotenv, ReportLab, OpenAI SDK, Anthropic SDK, pytest.

---

## 4. Folder Structure

```text
interview-prep-bot/
├── app.py                     # Streamlit entry point
├── requirements.txt
├── README.md
├── .env.example
├── .gitignore
│
├── config/
│   └── settings.py            # Reads .env, decides effective AI provider
│
├── ai/
│   ├── base.py                 # AIProvider ABC + Pydantic models
│   ├── openai_provider.py
│   ├── anthropic_provider.py
│   ├── mock_provider.py        # Powers Demo Mode
│   └── factory.py              # get_ai_provider() with automatic fallback
│
├── database/
│   ├── database.py             # engine/session
│   ├── models.py                # User, Interview, Question, Answer, Performance
│   └── crud.py
│
├── interview/
│   ├── interviewer.py          # InterviewSession orchestration
│   ├── evaluator.py
│   ├── question_generator.py
│   ├── difficulty.py           # Adaptive difficulty ladder
│   └── question_bank.py        # Loads data/question_bank.json
│
├── coding/
│   ├── problems.py              # Local coding-problem bank + test cases
│   ├── code_runner.py           # Docker-first, restricted-fallback safe execution
│   └── evaluator.py
│
├── reports/
│   └── pdf_report.py            # ReportLab PDF generation
│
├── ui/
│   ├── dashboard.py, profile.py, interview.py, coding.py,
│   └── history.py, analytics.py, reports.py, settings.py
│
├── utils/
│   └── logger.py                # File logging, no raw tracebacks to users
│
├── data/
│   └── question_bank.json       # 70+ local questions across Python/SQL/ML/DS/AI/Web/HR
│
├── tests/
│   ├── conftest.py              # Isolated temp SQLite DB per test run, mock AI forced
│   ├── test_database.py, test_ai.py, test_interview.py,
│   └── test_evaluator.py, test_reports.py
│
├── logs/                        # app.log written here
└── storage/                     # interview_prep.db written here
```

---

## 5. Installation (Windows)

**PowerShell:**

```powershell
python --version

python -m venv .venv

.venv\Scripts\Activate.ps1

python -m pip install --upgrade pip

pip install -r requirements.txt

streamlit run app.py
```

**Command Prompt (cmd.exe):**

```cmd
python --version

python -m venv .venv

.venv\Scripts\activate.bat

python -m pip install --upgrade pip

pip install -r requirements.txt

streamlit run app.py
```

The app opens automatically in your browser (usually `http://localhost:8501`).

### PowerShell execution-policy issue

If `Activate.ps1` fails with a message about running scripts being disabled, run this once in your **current PowerShell window only** (it doesn't change any system-wide setting permanently):

```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
```

Then re-run `.venv\Scripts\Activate.ps1`.

---

## 6. Environment Variables

Copy `.env.example` to `.env`:

```powershell
copy .env.example .env
```

```env
AI_PROVIDER=mock
OPENAI_API_KEY=
ANTHROPIC_API_KEY=
MODEL_NAME=
DATABASE_URL=sqlite:///storage/interview_prep.db
```

Never commit your real `.env` file — it's already in `.gitignore`.

---

## 7. API Configuration

### OpenAI

1. Get an API key from your OpenAI account.
2. In `.env`:
   ```env
   AI_PROVIDER=openai
   OPENAI_API_KEY=sk-...
   MODEL_NAME=gpt-4o-mini
   ```
3. Restart the app.

### Anthropic

1. Get an API key from your Anthropic account.
2. In `.env`:
   ```env
   AI_PROVIDER=anthropic
   ANTHROPIC_API_KEY=sk-ant-...
   MODEL_NAME=claude-sonnet-4-6
   ```
3. Restart the app.

If a key is missing or invalid, or a request fails, the app **automatically falls back to Demo Mode** rather than breaking — you'll see this reflected on the Settings page and in the sidebar badge.

---

## 8. Demo Mode

No API key at all? Leave `AI_PROVIDER=mock` (the default). The built-in `MockProvider`:

- Pulls realistic questions from the local 70+ question bank (Python, SQL, ML, Data Science, AI, Web Dev, HR)
- Scores answers using heuristics (length, structure, keyword signals) with slight randomness for variety
- Produces strengths, weaknesses, feedback, and an ideal answer for every question

This lets you fully exercise every feature — interviews, adaptive difficulty, coding mode, history, analytics, PDF reports — with zero setup.

---

## 9. Testing

```powershell
pip install -r requirements.txt
pytest -v
```

Tests run against an isolated temporary SQLite database (never your real `storage/interview_prep.db`) and force Demo Mode, so **no API key is required to run the test suite**. Covered: database init, user CRUD, interview/question/answer flow, adaptive difficulty, mock AI generation/evaluation, provider fallback, and PDF report generation.

---

## 10. How to Use

1. **Profile** — enter your name, target role, experience, skills, preferred technology, and save.
2. **Start Interview** — choose type, technology, difficulty, and question count, then click **START INTERVIEW**.
   - Choosing **Coding** as the interview type routes you to the **Coding Interview** page instead.
3. **Live Interview** — read the question, type your answer, submit. You'll see your score and feedback before moving to the next question. Difficulty adapts automatically unless you picked a fixed level.
4. At the end you get an **Interview Completed** summary with overall score, strong/weak areas, and a recommendation.
5. **History** — revisit any past interview in full detail.
6. **Analytics** — see trends and topic breakdowns across all your interviews.
7. **Reports** — generate and download a PDF report for any completed interview.
8. **Coding Interview** — pick or randomize a problem, write your solution, run it against test cases safely.
9. **Settings** — check which AI provider is active and adjust session defaults.

---

## 11. Coding Mode Safety Notes

Candidate code is **never executed directly, unrestricted, on your machine**:

- If **Docker** is installed and on your PATH, code runs inside a throwaway `python:3.11-slim` container with `--network none`, memory/CPU limits, and a read-only mount.
- If Docker is **not** available, the app falls back to a clearly-labeled **restricted demo mode**: a separate process, a 5-second timeout, and basic static screening for risky patterns (e.g. `import os`, `eval(`). This fallback is a best-effort safeguard for local practice — it is **not** a hardened security sandbox. For anything beyond personal local use, install [Docker Desktop](https://www.docker.com/products/docker-desktop/).

---

## 12. Troubleshooting

| Problem | Solution |
|---|---|
| `Activate.ps1 cannot be loaded` | Run `Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass` in that PowerShell window, then retry. |
| `streamlit: command not found` | Make sure the virtual environment is activated (`.venv\Scripts\Activate.ps1`) before running `streamlit run app.py`. |
| App says "Demo Mode" even though I set an API key | Double-check `.env` (not `.env.example`) has `AI_PROVIDER=openai` or `anthropic` **and** the matching key filled in, then fully restart `streamlit run app.py`. |
| `ModuleNotFoundError` | Run `pip install -r requirements.txt` again inside the activated virtual environment. |
| Coding mode says Docker not detected | Expected if Docker isn't installed — the app still works via the restricted fallback. Install Docker Desktop for full sandboxing. |
| Database looks empty after restart | Confirm `DATABASE_URL` in `.env` still points at `sqlite:///storage/interview_prep.db` — the tests use a different temporary DB and never touch this file. |
| PDF report fails to generate | Check `logs/app.log` for the underlying error; make sure `reportlab` installed correctly. |

Technical errors are always written to `logs/app.log` — check there first for anything not covered above.

---

## 13. Security

- All secrets live in `.env` (git-ignored), never hard-coded
- API keys are masked (`sk-a****...wxyz`) anywhere they're displayed in the UI
- All database access goes through SQLAlchemy's ORM (parameterized queries, no raw SQL string building)
- Candidate code execution is isolated per section 11 above
- Malformed AI responses are caught by Pydantic validation and never crash the app
- All exceptions are logged to file, never shown as raw tracebacks to the user

---

## 14. Future Upgrades

- Resume-based interview question generation
- Voice interviews with speech-to-text
- Facial-expression / body-language analysis
- Real-time communication/tone analysis
- RAG-based company-specific interview question sets
- Job description analysis for tailored prep
- Personalized learning roadmap generation
- LinkedIn / resume import integration
- PostgreSQL for multi-user deployments
- Full Docker Compose deployment (app + sandboxed code runner)
- User authentication and multi-tenant accounts
- Cloud deployment (Streamlit Community Cloud, AWS, Azure, GCP)

---

Built for interview practice — good luck! 🚀
