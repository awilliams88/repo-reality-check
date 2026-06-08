---
title: Repo Reality Check
emoji: 🔥
colorFrom: red
colorTo: red
sdk: gradio
sdk_version: 6.17.3
app_file: app.py
python_version: "3.12"
short_description: Code-health review that ends with fixes
pinned: false
tags:
- build-small-hackathon
- backyard-ai
- jetbrains
- openai
- off-brand
- best-agent
- sharing-is-caring
- code-review
---

# Repo Reality Check

Repo Reality Check turns bounded repository context into a useful code-health report:
repo pulse, top risks, quick wins, one sharp reality check, a prioritized fix plan, and
a public-safe share card.

## Model Plan

- Primary model: `JetBrains/Mellum2-12B-A2.5B-Instruct`
- Fallback model metadata: `openai/gpt-oss-20b`
- Speech input: `openai/whisper-small` local transcription for review goals
- Fine-tuned adapter: `build-small-hackathon/repo-reality-check-review-lora`
- Training: Modal A10G QLoRA on app-format code review examples
- Parameter cap: selected code model path stays under the 32B hackathon limit

The app reviews uploaded files and notes inside the local Space runtime. It does
not clone private repositories or send code to an external hosted review API.

## Hackathon Alignment

| Requirement | Repo Reality Check implementation |
|---|---|
| Gradio Space in `build-small-hackathon` | `build-small-hackathon/repo-reality-check` |
| Track | Backyard AI |
| Sponsor focus | JetBrains Mellum2 instruction model with OpenAI fallback metadata |
| Merit targets | Best Agent, Sharing is Caring, Off-Brand |
| Multimodal input | File uploads, typed repo notes, microphone review goal |
| Fine-tuning | Modal QLoRA adapter trained on app-format repo-review examples |
| Demo/social links | Add final demo video and social post links after recording |

## Links

- GitHub Repo: https://github.com/awilliams88/repo-reality-check
- Hugging Face Space: https://huggingface.co/spaces/build-small-hackathon/repo-reality-check
- Fine-tuned Model: https://huggingface.co/build-small-hackathon/repo-reality-check-review-lora
- Demo Video: pending final recording
- Social Post: pending final post

## Local Development

```bash
./run.sh setup
./run.sh app
./run.sh verify
```

## Codebase

| Path | Purpose |
|---|---|
| `app.py` | Hugging Face Spaces entry point |
| `env/` | Runtime patches, constants, model IDs, links |
| `core/` | File ingestion, speech transcription, inference, section parsing |
| `ui/` | Gradio review layout, examples, custom terminal CSS |
| `modal/` | Modal QLoRA training job, synthetic dataset, model card |

## Limits

Repo Reality Check only reviews files supplied by the user, with bounded file count
and byte limits. It should not invent line numbers, private repo state, or
security findings beyond the provided context.

## Training Data

The Modal dataset covers Space submission checks, API reliability, frontend
responsiveness, GPU training persistence, architecture boundaries, and README
submission metadata. The output target is the current production UI format.
