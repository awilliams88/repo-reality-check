from __future__ import annotations

import os
from env.runtime import patch_asyncio_cleanup_warning
from ui.layout import create_app, get_theme
from ui.styles import CUSTOM_CSS

# Keep custom Gradio CSS stable in the Space runtime.
os.environ.setdefault("GRADIO_SSR_MODE", "false")

# Hide a harmless local Gradio teardown warning.
patch_asyncio_cleanup_warning()

# Build the Space app once for discovery.
demo = create_app()

if __name__ == "__main__":
    # Direct launch is used by run.sh and Hugging Face Spaces.
    demo.launch(theme=get_theme(), css=CUSTOM_CSS)
