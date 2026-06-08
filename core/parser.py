from __future__ import annotations

from pathlib import Path
import re
from typing import Any

from env.config import BYTES_PER_FILE_LIMIT, FILE_LIMIT, SUPPORTED_SUFFIXES

# Match code review output sections expected by the UI.
_SECTION_PATTERN = re.compile(
    r"(?im)^[ \t]*(?:#{1,6}[ \t]*)?(?:={2,}[ \t]*)?"
    r"(?P<label>repo pulse|top risks?|quick wins?|sharp roast|fix plan|share card)"
    r"\b(?:[ \t]*={2,})?[ \t]*(?::|-)?[ \t]*(?P<trailing>[^\n]*)$"
)

_ORDER = ("pulse", "risks", "wins", "roast", "plan", "card")
_DEFAULTS = {
    "pulse": "Upload a few files or paste repository notes to begin.",
    "risks": "- No risks analyzed yet.",
    "wins": "- No quick wins analyzed yet.",
    "roast": "No roast yet.",
    "plan": "No fix plan yet.",
    "card": "Share card will appear here.",
}


def resolve_paths(file_input: object | None) -> list[Path]:
    """Normalizes Gradio file payload variants into local paths."""
    # Empty uploads are valid when notes are pasted.
    if not file_input:
        return []
    if isinstance(file_input, (list, tuple)):
        paths: list[Path] = []
        for item in file_input:
            paths.extend(resolve_paths(item))
        return paths
    if isinstance(file_input, dict):
        for key in ("path", "name", "orig_name"):
            value = file_input.get(key)
            if value:
                return [Path(str(value))]
        return []
    return [Path(str(file_input))]


def stringify_content(content: Any) -> str:
    """Converts Gradio content variants into prompt-safe text."""
    # Plain textbox values arrive as strings.
    if content is None:
        return ""
    if isinstance(content, str):
        return content.strip()
    if isinstance(content, (list, tuple)):
        parts = [stringify_content(item) for item in content]
        return " ".join(part for part in parts if part).strip()
    if isinstance(content, dict):
        for key in ("text", "value", "path", "url", "name", "alt_text"):
            value = content.get(key)
            if value:
                return stringify_content(value)
        return ""
    return str(content).strip()


def read_repo_files(file_input: object | None) -> tuple[str, str]:
    """Reads selected repo files into a bounded review context."""
    # Limit both file count and bytes per file for predictable local inference.
    chunks: list[str] = []
    logs: list[str] = []
    for path in resolve_paths(file_input)[:FILE_LIMIT]:
        suffix = path.suffix.lower()
        if suffix not in SUPPORTED_SUFFIXES:
            logs.append(f"Skipped unsupported file: {path.name}")
            continue
        try:
            raw = path.read_bytes()[:BYTES_PER_FILE_LIMIT]
            text = raw.decode("utf-8", errors="ignore")
            chunks.append(f"--- FILE: {path.name} ---\n{text}")
            logs.append(f"Read {path.name} ({len(raw)} bytes).")
        except Exception as exc:
            logs.append(f"Could not read {path.name}: {exc}")
    if not chunks:
        logs.append("No supported files were read.")
    return "\n\n".join(chunks), "\n".join(logs)


def _canonical(label: str) -> str:
    """Maps heading variants onto code-health cards."""
    normalized = label.lower()
    if "pulse" in normalized:
        return "pulse"
    if "risk" in normalized:
        return "risks"
    if "win" in normalized:
        return "wins"
    if "roast" in normalized:
        return "roast"
    if "plan" in normalized:
        return "plan"
    return "card"


def parse_sections(response: str) -> tuple[str, str, str, str, str, str]:
    """Extracts repository review sections from model output."""
    # Keep defaults stable when a model misses a section.
    matches = list(_SECTION_PATTERN.finditer(response))
    sections = dict(_DEFAULTS)
    if not matches:
        if response.strip():
            sections["pulse"] = response.strip()
        return (
            sections["pulse"],
            sections["risks"],
            sections["wins"],
            sections["roast"],
            sections["plan"],
            sections["card"],
        )
    for index, match in enumerate(matches):
        key = _canonical(match.group("label"))
        next_start = (
            matches[index + 1].start() if index + 1 < len(matches) else len(response)
        )
        value = "\n".join(
            [match.group("trailing"), response[match.end() : next_start]]
        ).strip()
        if value:
            sections[key] = value
    return (
        sections["pulse"],
        sections["risks"],
        sections["wins"],
        sections["roast"],
        sections["plan"],
        sections["card"],
    )
