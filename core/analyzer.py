from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass
from typing import Any

try:
    import spaces
except ImportError:
    # Use a no-op GPU decorator during local development.
    class _LocalSpacesFallback:
        @staticmethod
        def GPU(
            duration: int = 45,
        ) -> Callable[[Callable[..., Any]], Callable[..., Any]]:
            def decorator(function: Callable[..., Any]) -> Callable[..., Any]:
                return function

            return decorator

    spaces = _LocalSpacesFallback()

from core.inference import run_review_inference, transcribe_audio
from core.parser import parse_sections, read_repo_files, stringify_content
from env.config import MODEL_ID, PARAMETER_COUNT, PROMPT_LIMIT

# Review prompt keeps the roast useful and concrete.
REVIEW_PROMPT = (
    "You are Roast My Repo, a senior code reviewer with a dry but constructive tone. "
    "Prioritize bugs, risks, deployment gaps, missing tests, unclear architecture, and fast fixes. "
    "Do not invent files or line numbers. Be funny only after being useful. "
    "Never include secrets from the provided code. Keep output concise and actionable."
)


@dataclass(frozen=True)
class RepoReview:
    """Structure containing source context, execution logs, and parsed review output."""

    context: str
    logs: str
    pulse: str
    risks: str
    wins: str
    roast: str
    plan: str
    card: str


def build_review_prompt(
    repo_context: str,
    notes: str,
    voice_goal: str,
    review_depth: str,
    tone: str,
) -> str:
    """Builds the app-format code review prompt."""
    return f"""{REVIEW_PROMPT}

Review depth: {review_depth}
Tone: {tone}
User notes:
{notes}

Voice goal:
{voice_goal}

Repository context:
{repo_context[:PROMPT_LIMIT]}

Return exactly these sections:

=== REPO PULSE ===
[2-3 sentence high-level read.]

=== TOP RISKS ===
- [Most important concrete risks.]

=== QUICK WINS ===
- [Small changes with high leverage.]

=== SHARP ROAST ===
[One funny but accurate paragraph.]

=== FIX PLAN ===
1. [Prioritized implementation plan.]

=== SHARE CARD ===
[A short public-safe summary suitable for posting.]
"""


def review_repo(
    files: object | None,
    notes: Any,
    voice_goal: object | None,
    review_depth: str,
    tone: str,
) -> RepoReview:
    """Orchestrates file ingestion, speech transcription, inference, and parsing."""
    # Bound the repository context before passing it into the model.
    repo_context, file_log = read_repo_files(files)
    note_text = stringify_content(notes)
    transcript, transcript_log = transcribe_audio(voice_goal)
    if not repo_context and note_text:
        repo_context = f"--- USER NOTES ONLY ---\n{note_text}"
    prompt = build_review_prompt(
        repo_context,
        note_text,
        transcript,
        review_depth,
        tone,
    )
    response, inference_log = run_review_inference(prompt)
    pulse, risks, wins, roast, plan, card = parse_sections(response)
    logs = "\n".join(
        [
            f"Primary model: {MODEL_ID}",
            f"Parameters: {PARAMETER_COUNT}",
            "Execution flow: local Space runtime; no repo contents sent to external APIs",
            "---",
            file_log,
            transcript_log,
            inference_log,
        ]
    )
    context = "\n".join(
        part
        for part in [
            f"Review depth: {review_depth}",
            f"Tone: {tone}",
            f"Notes: {note_text}" if note_text else "",
            f"Voice goal: {transcript}" if transcript else "",
            file_log,
        ]
        if part
    )
    return RepoReview(context, logs, pulse, risks, wins, roast, plan, card)


@spaces.GPU(duration=60)
def review_repo_ui(
    files: object | None,
    notes: Any,
    voice_goal: object | None,
    review_depth: str,
    tone: str,
) -> tuple[str, str, str, str, str, str, str, str]:
    """Gradio-compatible entry point for repo review generation."""
    # Convert the review report into component outputs.
    review = review_repo(files, notes, voice_goal, review_depth, tone)
    return (
        review.context,
        review.logs,
        review.pulse,
        review.risks,
        review.wins,
        review.roast,
        review.plan,
        review.card,
    )


def reset_outputs() -> tuple[str, str, str, str, str, str, str, str]:
    """Clears outputs before a new repo review."""
    # Keep click feedback immediate while the model loads.
    return (
        "Reading repository context...",
        "Starting local review model...",
        "",
        "",
        "",
        "",
        "",
        "",
    )
