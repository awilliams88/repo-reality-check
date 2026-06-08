from __future__ import annotations

import asyncio.base_events as base_events
import os
from pathlib import Path
from typing import Any


def patch_asyncio_cleanup_warning() -> None:
    """Keeps local Gradio teardown from surfacing a known invalid-fd warning."""
    # Skip patching when this Python runtime does not expose the cleanup hook.
    original_del = getattr(base_events.BaseEventLoop, "__del__", None)
    if original_del is None or getattr(original_del, "_roast_repo_patched", False):
        return

    # Preserve normal cleanup while ignoring the harmless invalid-fd case.
    def patched_del(self: Any) -> None:
        try:
            original_del(self)
        except ValueError as exc:
            if str(exc) != "Invalid file descriptor: -1":
                raise

    # Mark the function so repeated imports stay idempotent.
    setattr(patched_del, "_roast_repo_patched", True)
    setattr(base_events.BaseEventLoop, "__del__", patched_del)


def load_env() -> None:
    """Loads simple KEY=value pairs from local .env files."""
    # Search the project folder before the parent workspace.
    for path in [Path(".env"), Path("../.env")]:
        if path.is_file():
            try:
                with open(path, encoding="utf-8") as f:
                    for line in f:
                        line = line.strip()
                        if line and not line.startswith("#") and "=" in line:
                            key, value = line.split("=", 1)
                            os.environ.setdefault(
                                key.strip(), value.strip().strip("'\"")
                            )
                break
            except Exception:
                pass


# Load local tokens before model loading.
load_env()
