"""
Safe(r) execution of candidate-submitted Python code against test
cases.

Per the project requirements, arbitrary candidate code must NOT be
executed directly and unrestricted on the host machine. This module:

1. Prefers running the code inside a throwaway Docker container
   (`python:3.11-slim`) with no network access, a read-only
   filesystem, and CPU/memory/time limits, if Docker is available.
2. If Docker is not available, falls back to a clearly-labeled
   restricted subprocess mode: a separate OS process, no network
   assumptions handled at this layer, a hard wall-clock timeout, and
   basic static screening of the source for obviously dangerous
   imports/calls. This fallback is a best-effort demo safeguard, NOT
   a security sandbox — the UI clearly tells the user this.

Docker is the recommended safe path for anything beyond local demo
use.
"""
import json
import shutil
import subprocess
import tempfile
import textwrap
from pathlib import Path
from typing import List, Dict, Any

_BLOCKED_PATTERNS = [
    "import os",
    "import sys",
    "import subprocess",
    "import shutil",
    "import socket",
    "__import__",
    "open(",
    "eval(",
    "exec(",
    "importlib",
]

_TIMEOUT_SECONDS = 5


def docker_available() -> bool:
    return shutil.which("docker") is not None


def _static_screen(code: str) -> List[str]:
    warnings = []
    for pattern in _BLOCKED_PATTERNS:
        if pattern in code:
            warnings.append(f"Potentially unsafe usage detected: '{pattern.strip()}'")
    return warnings


def _build_harness(candidate_code: str, function_name: str, test_cases: List[Dict[str, Any]]) -> str:
    """
    Wraps the candidate's code + test cases into a single script that
    prints a JSON summary of pass/fail results to stdout.
    """
    tests_literal = json.dumps(test_cases)
    return textwrap.dedent(
        f"""
        import json, time, traceback

        results = []
        tests = json.loads('''{tests_literal}''')

        {candidate_code}

        for t in tests:
            case_result = {{"input": t.get("input"), "expected": t.get("expected")}}
            try:
                start = time.time()
                args = t.get("input")
                if isinstance(args, list):
                    output = {function_name}(*args)
                elif isinstance(args, dict):
                    output = {function_name}(**args)
                else:
                    output = {function_name}(args)
                elapsed = time.time() - start
                case_result["output"] = output
                case_result["passed"] = (output == t.get("expected"))
                case_result["time_seconds"] = round(elapsed, 6)
            except Exception as e:
                case_result["output"] = None
                case_result["passed"] = False
                case_result["error"] = f"{{type(e).__name__}}: {{e}}"
            results.append(case_result)

        print("###RESULTS_START###")
        print(json.dumps(results))
        print("###RESULTS_END###")
        """
    )


def _parse_output(raw: str) -> List[Dict[str, Any]]:
    try:
        start = raw.index("###RESULTS_START###") + len("###RESULTS_START###")
        end = raw.index("###RESULTS_END###")
        payload = raw[start:end].strip()
        return json.loads(payload)
    except Exception:
        return []


def _run_in_subprocess(script_path: Path) -> subprocess.CompletedProcess:
    return subprocess.run(
        ["python", str(script_path)],
        capture_output=True,
        text=True,
        timeout=_TIMEOUT_SECONDS,
    )


def _run_in_docker(script_path: Path) -> subprocess.CompletedProcess:
    return subprocess.run(
        [
            "docker", "run", "--rm",
            "--network", "none",
            "--memory", "128m",
            "--cpus", "0.5",
            "--read-only",
            "-v", f"{script_path.parent}:/sandbox:ro",
            "python:3.11-slim",
            "python", f"/sandbox/{script_path.name}",
        ],
        capture_output=True,
        text=True,
        timeout=_TIMEOUT_SECONDS + 10,
    )


def run_candidate_code(
    candidate_code: str, function_name: str, test_cases: List[Dict[str, Any]]
) -> Dict[str, Any]:
    """
    Returns a dict:
    {
      "mode": "docker" | "restricted-subprocess",
      "warnings": [...],
      "results": [ {input, expected, output, passed, error?, time_seconds?} ],
      "passed_count": int,
      "total_count": int,
      "stderr": str,
      "success": bool
    }
    """
    warnings = _static_screen(candidate_code)
    harness = _build_harness(candidate_code, function_name, test_cases)

    with tempfile.TemporaryDirectory() as tmp:
        script_path = Path(tmp) / "candidate_script.py"
        script_path.write_text(harness, encoding="utf-8")

        use_docker = docker_available()
        mode = "docker" if use_docker else "restricted-subprocess"

        try:
            if use_docker:
                proc = _run_in_docker(script_path)
            else:
                proc = _run_in_subprocess(script_path)
        except subprocess.TimeoutExpired:
            return {
                "mode": mode,
                "warnings": warnings,
                "results": [],
                "passed_count": 0,
                "total_count": len(test_cases),
                "stderr": "Execution timed out.",
                "success": False,
            }
        except Exception as exc:
            return {
                "mode": mode,
                "warnings": warnings,
                "results": [],
                "passed_count": 0,
                "total_count": len(test_cases),
                "stderr": f"Execution failed to start: {exc}",
                "success": False,
            }

        results = _parse_output(proc.stdout)
        passed_count = sum(1 for r in results if r.get("passed"))

        return {
            "mode": mode,
            "warnings": warnings,
            "results": results,
            "passed_count": passed_count,
            "total_count": len(test_cases),
            "stderr": proc.stderr[-2000:] if proc.stderr else "",
            "success": len(results) > 0,
        }
