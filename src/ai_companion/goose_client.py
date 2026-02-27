from __future__ import annotations

import json
import os
import shutil
import subprocess
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ai_companion.config import Settings


def _find_goose_exe() -> str:
    """
    Find goose executable in a Windows-friendly way.
    Priority:
      1) GOOSE_EXE env var (explicit)
      2) PATH via shutil.which
      3) common default install location: %USERPROFILE%/.local/bin/goose.exe
    """
    explicit = os.getenv("GOOSE_EXE")
    if explicit and os.path.exists(explicit):
        return explicit

    found = shutil.which("goose") or shutil.which("goose.exe")
    if found:
        return found

    candidate = os.path.join(os.path.expanduser("~"), ".local", "bin", "goose.exe")
    if os.path.exists(candidate):
        return candidate

    raise FileNotFoundError(
        "Could not find goose executable. "
        "Run `where.exe goose` in PowerShell to locate it, "
        "then set environment variable GOOSE_EXE to that full path."
    )


def goose_answer(prompt: str, settings: "Settings", timeout_s: int = 120) -> str:
    goose_exe = _find_goose_exe()

    cmd = [
        goose_exe,
        "run",
        "--no-session",
        "--output-format",
        "json",
    ]

    if settings.llm_provider:
        cmd += ["--provider", settings.llm_provider]
    if settings.llm_model:
        cmd += ["--model", settings.llm_model]
    if settings.identity_system_prompt:
        cmd += ["--system", settings.identity_system_prompt]

    cmd += ["-t", prompt]

    proc = subprocess.run(
        cmd,
        text=True,
        capture_output=True,
        timeout=timeout_s,
    )

    # Prefer stdout, but if it's empty sometimes goose writes to stderr
    out = (proc.stdout or "").strip()
    err = (proc.stderr or "").strip()

    if proc.returncode != 0:
        detail = err or out or f"exit code {proc.returncode}"
        return f"[goose error] {detail}"

    # If stdout is empty, still surface stderr (some versions print there)
    if not out and err:
        # If stderr contains JSON, we'll parse it below; otherwise return it.
        out = err

    # Goose sometimes prints banners + JSON; parse from first '{'
    json_start = out.find("{")
    if json_start == -1:
        # No JSON found; return whatever we got so you can see it
        detail = out or err or "No output from goose."
        return f"[goose error] Expected JSON but got:\n{detail}"

    raw_json = out[json_start:]

    try:
        payload = json.loads(raw_json)
    except json.JSONDecodeError as e:
        # Return tail to debug without crashing
        tail = raw_json[:1000]
        return f"[goose error] Could not parse JSON ({e}). Output starts with:\n{tail}"

    # Return the last assistant text chunk
    for msg in reversed(payload.get("messages", [])):
        if msg.get("role") == "assistant":
            for part in msg.get("content", []):
                if part.get("type") == "text":
                    text = (part.get("text") or "").strip()
                    if text:
                        return text

    return "[goose error] No assistant response found in JSON."

