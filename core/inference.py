from __future__ import annotations

import os
import re
from typing import Any

from env.config import ADAPTER_REPO_ID, FALLBACK_MODEL_ID, MODEL_ID, SPEECH_MODEL_ID

# Keep local model instances warm after first use.
_model: Any = None
_tokenizer: Any = None
_speech_pipeline: Any = None
_adapter_applied = False

_THINK_PATTERN = re.compile(r"<think>.*?</think>", re.IGNORECASE | re.DOTALL)


def clean_generated_text(text: str) -> str:
    """Removes hidden reasoning and chat-template leftovers from generated review text."""
    # Code review output should be visible, concise, and sectioned.
    text = _THINK_PATTERN.sub("", text)
    if "</think>" in text.lower():
        text = re.split(r"</think>", text, flags=re.IGNORECASE, maxsplit=1)[-1]
    for marker in ("<|im_end|>", "<|im_start|>", "\nUser:", "\nAssistant:"):
        if marker in text:
            text = text.split(marker, 1)[0]
    text = re.sub(r"[ \t]+", " ", text)
    text = "\n".join(line.strip() for line in text.splitlines())
    return re.sub(r"\n{3,}", "\n\n", text).strip()


def transcribe_audio(audio_path: object | None) -> tuple[str, str]:
    """Transcribes optional voice goals for the repo review."""
    global _speech_pipeline
    if not audio_path:
        return "", "No microphone review goal provided."
    try:
        from transformers import pipeline

        if _speech_pipeline is None:
            _speech_pipeline = pipeline(
                "automatic-speech-recognition",
                model=SPEECH_MODEL_ID,
                token=os.environ.get("HF_TOKEN"),
            )
        result = _speech_pipeline(str(audio_path))
        return str(
            result.get("text", "")
        ).strip(), f"Transcribed with {SPEECH_MODEL_ID}."
    except Exception as exc:
        return "", f"Speech transcription unavailable: {exc}"


def _format_chat_prompt(tokenizer: Any, messages: list[dict[str, str]]) -> str:
    """Formats messages while disabling hidden reasoning when supported."""
    try:
        return tokenizer.apply_chat_template(
            messages,
            tokenize=False,
            add_generation_prompt=True,
            enable_thinking=False,
        )
    except TypeError:
        return tokenizer.apply_chat_template(
            messages,
            tokenize=False,
            add_generation_prompt=True,
        )


def _load_model(log_lines: list[str]) -> tuple[Any, Any]:
    """Loads and caches the local code-review model."""
    global _adapter_applied, _model, _tokenizer
    if _model is None:
        import torch
        from peft import PeftModel
        from transformers import AutoModelForCausalLM, AutoTokenizer

        # Prefer the JetBrains model slug, with an OpenAI open-weight fallback if unavailable.
        selected_model = os.environ.get("ROAST_MODEL_ID", MODEL_ID)
        log_lines.append(f"Loading tokenizer: {selected_model}")
        _tokenizer = AutoTokenizer.from_pretrained(
            selected_model,
            trust_remote_code=True,
            token=os.environ.get("HF_TOKEN"),
        )
        dtype = torch.bfloat16 if torch.cuda.is_available() else torch.float32
        log_lines.append(f"Loading model: {selected_model}")
        try:
            _model = AutoModelForCausalLM.from_pretrained(
                selected_model,
                dtype=dtype,
                low_cpu_mem_usage=True,
                trust_remote_code=True,
                token=os.environ.get("HF_TOKEN"),
            )
        except Exception as exc:
            log_lines.append(f"Primary load failed: {exc}")
            log_lines.append(f"Loading fallback model: {FALLBACK_MODEL_ID}")
            _tokenizer = AutoTokenizer.from_pretrained(
                FALLBACK_MODEL_ID,
                trust_remote_code=True,
                token=os.environ.get("HF_TOKEN"),
            )
            _model = AutoModelForCausalLM.from_pretrained(
                FALLBACK_MODEL_ID,
                dtype=dtype,
                low_cpu_mem_usage=True,
                trust_remote_code=True,
                token=os.environ.get("HF_TOKEN"),
            )
        try:
            log_lines.append(f"Loading review LoRA adapter: {ADAPTER_REPO_ID}")
            _model = PeftModel.from_pretrained(
                _model,
                ADAPTER_REPO_ID,
                token=os.environ.get("HF_TOKEN"),
            )
            _adapter_applied = True
            log_lines.append("Review LoRA adapter applied.")
        except Exception as exc:
            _adapter_applied = False
            log_lines.append(f"Review adapter unavailable: {exc}")
        if torch.cuda.is_available():
            _model = _model.to("cuda")
    else:
        adapter_status = "with LoRA adapter" if _adapter_applied else "without adapter"
        log_lines.append(f"Using cached review model {adapter_status}.")
    return _model, _tokenizer


def run_review_inference(prompt: str) -> tuple[str, str]:
    """Executes local code review inference with a deterministic fallback."""
    log_lines: list[str] = []
    try:
        model, tokenizer = _load_model(log_lines)
        device = str(model.device)
        text = _format_chat_prompt(tokenizer, [{"role": "user", "content": prompt}])
        inputs = tokenizer([text], return_tensors="pt").to(device)
        generated_ids = model.generate(
            **inputs,
            max_new_tokens=760,
            do_sample=False,
            repetition_penalty=1.08,
        )
        generated_ids = [
            output_ids[len(input_ids) :]
            for input_ids, output_ids in zip(inputs.input_ids, generated_ids)
        ]
        response = tokenizer.batch_decode(generated_ids, skip_special_tokens=True)[0]
        log_lines.append("Local repo review completed.")
        return clean_generated_text(response), "\n".join(log_lines)
    except Exception as exc:
        log_lines.append(f"Local model execution failed: {exc}")
        log_lines.append("Returning deterministic repo review fallback.")
        return _fallback_review(prompt), "\n".join(log_lines)


def _fallback_review(prompt: str) -> str:
    """Returns a stable code-health report when model weights are unavailable."""
    return (
        "=== REPO PULSE ===\n"
        "The repo context was received, but the local model is still loading or unavailable. The fallback review focuses on structural hygiene.\n\n"
        "=== TOP RISKS ===\n"
        "- Missing automated verification will make regressions hard to catch.\n"
        "- Large files or mixed concerns can hide ownership boundaries.\n"
        "- Deployment docs need to match the actual run path.\n\n"
        "=== QUICK WINS ===\n"
        "- Add one command that runs format, lint, type checks, and compile checks.\n"
        "- Keep environment constants out of UI code.\n"
        "- Write a README table that maps each module to its responsibility.\n\n"
        "=== REALITY CHECK ===\n"
        "Right now the repo is giving 'works on my laptop, emotionally' energy. The fix is boring in the best way: one clean entry point, one verification command, and fewer mystery files.\n\n"
        "=== FIX PLAN ===\n"
        "1. Add or repair the run script.\n"
        "2. Split runtime constants, core logic, and UI wiring.\n"
        "3. Add a smoke test or compile check for every app module.\n\n"
        "=== SHARE CARD ===\n"
        f"Code-health review generated from bounded local context. Prompt sample: {prompt[:180]}"
    )
