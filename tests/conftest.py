"""
Shared pytest setup.

We set AI_PROVIDER=mock and point DATABASE_URL at a fresh temporary
SQLite file *before* any application module is imported, by doing
this work in pytest_configure (which pytest runs before collecting
and importing test modules). This guarantees tests never touch the
real storage/interview_prep.db and always run in Demo Mode, with no
API key required.
"""
import os
import tempfile


def pytest_configure(config):
    tmp_dir = tempfile.mkdtemp(prefix="interview_prep_tests_")
    db_path = os.path.join(tmp_dir, "test.db")
    os.environ["DATABASE_URL"] = f"sqlite:///{db_path}"
    os.environ["AI_PROVIDER"] = "mock"
    os.environ["OPENAI_API_KEY"] = ""
    os.environ["ANTHROPIC_API_KEY"] = ""

    # Import here (after env vars are set) so the engine is created
    # against the temp database from the very first import.
    from database.database import init_db

    init_db()
