from __future__ import annotations

# App copy shown in the Gradio header.
APP_TITLE = "Roast My Repo"
APP_DESCRIPTION = "A useful code-health roast that ends with fixes, not vibes."

# Input limits keep local review prompts auditable.
FILE_LIMIT = 12
BYTES_PER_FILE_LIMIT = 18000
PROMPT_LIMIT = 28000
SUPPORTED_SUFFIXES = {
    ".py",
    ".js",
    ".ts",
    ".tsx",
    ".jsx",
    ".go",
    ".rs",
    ".java",
    ".md",
    ".json",
    ".yaml",
    ".yml",
    ".toml",
    ".sh",
}

# Public links shown in the Space footer.
GITHUB_URL = "https://github.com/awilliams88/roast-my-repo"
SPACE_URL = "https://huggingface.co/spaces/build-small-hackathon/roast-my-repo"

# Model metadata keeps docs, logs, and UI aligned.
MODEL_ID = "JetBrains/Mellum2-12B-A2.5B-Instruct"
FALLBACK_MODEL_ID = "openai/gpt-oss-20b"
ADAPTER_REPO_ID = "build-small-hackathon/roast-my-repo-review-lora"
SPEECH_MODEL_ID = "openai/whisper-small"
SPONSOR_NAME = "JetBrains / OpenAI"
PARAMETER_COUNT = "Under 32B"
