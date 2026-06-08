from __future__ import annotations

from html import escape
import gradio as gr

# Example review briefs populate notes without uploading files.
EXAMPLE_CARDS = [
    {
        "title": "Hackathon Space",
        "depth": "Submission-ready",
        "notes": "Review a Gradio Space for structure, missing verification, README accuracy, and deployment risks.",
    },
    {
        "title": "Tiny API",
        "depth": "Bug hunt",
        "notes": "Look for request validation, error handling, auth assumptions, and tests around edge cases.",
    },
    {
        "title": "Frontend Tool",
        "depth": "UX + code",
        "notes": "Check component boundaries, state handling, responsive layout, and whether the main workflow is complete.",
    },
]


def _card_html(title: str, depth: str, notes: str) -> str:
    """Builds a compact repo review preset."""
    return (
        '<div class="rr-example-copy">'
        '<div class="rr-example-head">'
        f"<span>{escape(title)}</span>"
        f"<strong>{escape(depth)}</strong>"
        "</div>"
        f"<p>{escape(notes)}</p>"
        "</div>"
    )


def _select_example(notes: str, depth: str) -> tuple[str, str]:
    """Populates notes and review-depth controls from an example."""
    return notes, depth


def render_examples(notes_input: gr.Textbox, depth_input: gr.Dropdown) -> gr.Column:
    """Renders review brief examples and wires buttons."""
    with gr.Column(elem_classes=["rr-examples-section"]) as section:
        gr.Markdown("## Review Briefs")
        with gr.Row(elem_classes=["rr-example-grid"]):
            for example in EXAMPLE_CARDS:
                with gr.Column(elem_classes=["rr-example-card"]):
                    gr.HTML(
                        _card_html(
                            str(example["title"]),
                            str(example["depth"]),
                            str(example["notes"]),
                        )
                    )
                    use_example = gr.Button(
                        "Use brief",
                        size="sm",
                        elem_classes=["rr-example-btn"],
                    )
                    use_example.click(
                        fn=lambda notes=str(example["notes"]), depth=str(example["depth"]): (
                            _select_example(notes, depth)
                        ),
                        inputs=[],
                        outputs=[notes_input, depth_input],
                        queue=False,
                    )
    return section
