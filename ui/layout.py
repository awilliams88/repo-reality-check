from __future__ import annotations

from typing import Any
import gradio as gr
from gradio.themes import Soft

from core.analyzer import reset_outputs, review_repo_ui
from env.config import APP_DESCRIPTION, APP_TITLE, GITHUB_URL, SPACE_URL
from ui.examples import render_examples


def get_theme() -> Any:
    """Returns the custom soft theme configured for code-review lime styling."""
    # Use lime on charcoal so this project differs from the other Spaces.
    return Soft(primary_hue="lime", secondary_hue="red", neutral_hue="zinc")


def create_app() -> gr.Blocks:
    """Creates and lays out the Gradio interface for Roast My Repo."""
    with gr.Blocks(title=APP_TITLE) as demo:
        # Header makes the code review workflow immediately available.
        gr.Markdown(f"# {APP_TITLE}\n{APP_DESCRIPTION}", elem_id="rr-header")
        gr.Markdown(
            "Upload source files, paste repo notes, or speak the review goal. Get risks, quick wins, a roast, and a fix plan.",
            elem_id="rr-kicker",
        )

        with gr.Row(elem_classes=["rr-main-grid"]):
            # Left column gathers bounded repository context.
            with gr.Column(scale=1, elem_classes=["rr-input-panel"]):
                gr.Markdown("## Repo Context")
                files_input = gr.File(
                    label="Upload source/docs files",
                    file_count="multiple",
                    elem_classes=["rr-file-input"],
                )
                notes_input = gr.Textbox(
                    label="Repo notes or URL",
                    lines=6,
                    placeholder="Paste README excerpts, repo goals, failing behavior, or a GitHub URL for context.",
                    elem_id="rr-notes-input",
                )
                voice_input = gr.Audio(
                    label="Speak the review goal",
                    sources=["microphone", "upload"],
                    type="filepath",
                    elem_classes=["rr-audio-input"],
                )
                with gr.Row(elem_classes=["rr-control-row"]):
                    depth_input = gr.Dropdown(
                        ["Submission-ready", "Bug hunt", "Architecture", "UX + code"],
                        value="Submission-ready",
                        label="Review depth",
                    )
                    tone_input = gr.Radio(
                        ["Direct", "Spicy", "Executive"],
                        value="Direct",
                        label="Tone",
                    )
                run_button = gr.Button(
                    "Roast Repo",
                    variant="primary",
                    elem_classes=["rr-run-btn"],
                )

            # Right column shows high-signal review cards.
            with gr.Column(scale=1, elem_classes=["rr-output-panel"]):
                gr.Markdown("## Code Health")
                pulse_output = gr.Textbox(
                    label="Repo Pulse",
                    lines=5,
                    interactive=False,
                    elem_classes=["rr-output-card", "rr-pulse-card"],
                )
                risks_output = gr.Textbox(
                    label="Top Risks",
                    lines=7,
                    interactive=False,
                    elem_classes=["rr-output-card", "rr-risks-card"],
                )
                wins_output = gr.Textbox(
                    label="Quick Wins",
                    lines=7,
                    interactive=False,
                    elem_classes=["rr-output-card", "rr-wins-card"],
                )

        with gr.Column(elem_classes=["rr-analysis-section"]):
            gr.Markdown("## Fix Desk")
            with gr.Row(elem_classes=["rr-card-grid"]):
                roast_output = gr.Textbox(
                    label="Sharp Roast",
                    lines=6,
                    interactive=False,
                    elem_classes=["rr-output-card", "rr-roast-card"],
                )
                plan_output = gr.Textbox(
                    label="Fix Plan",
                    lines=8,
                    interactive=False,
                    elem_classes=["rr-output-card", "rr-plan-card"],
                )
            card_output = gr.Textbox(
                label="Share Card",
                lines=5,
                interactive=False,
                elem_classes=["rr-output-card", "rr-share-card"],
            )

        render_examples(notes_input, depth_input)

        gr.Markdown(
            f"[GitHub repo]({GITHUB_URL}) | [Hugging Face Space]({SPACE_URL})",
            elem_id="rr-links",
        )

        with gr.Accordion("Diagnostics & Local Execution Logs", open=False):
            context_output = gr.Textbox(
                label="Review context",
                lines=5,
                interactive=False,
                elem_classes=["rr-log-box"],
            )
            model_output = gr.Textbox(
                label="System execution logs",
                lines=6,
                interactive=False,
                elem_classes=["rr-log-box"],
            )

        # Reset outputs immediately, then dispatch to the local review model.
        reset_event = run_button.click(
            fn=reset_outputs,
            inputs=[],
            outputs=[
                context_output,
                model_output,
                pulse_output,
                risks_output,
                wins_output,
                roast_output,
                plan_output,
                card_output,
            ],
            queue=False,
        )
        reset_event.then(
            fn=review_repo_ui,
            inputs=[
                files_input,
                notes_input,
                voice_input,
                depth_input,
                tone_input,
            ],
            outputs=[
                context_output,
                model_output,
                pulse_output,
                risks_output,
                wins_output,
                roast_output,
                plan_output,
                card_output,
            ],
        )

    return demo
