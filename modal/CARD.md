---
base_model: JetBrains/Mellum2-12B-A2.5B-Instruct
library_name: peft
pipeline_tag: text-generation
language:
- en
tags:
- peft
- lora
- code-review
- jetbrains
- openai
- build-small-hackathon
---

# Roast My Repo Review LoRA

Roast My Repo Review LoRA is a QLoRA adapter planned for the Roast My Repo
Space. It teaches a compact code-review model to produce useful, shareable repo
health reports with a dry but constructive tone.

## Intended Use

- Code-health summaries for small repositories
- Hackathon submission readiness checks
- Architecture and verification risk review
- Shareable public-safe roast cards

## Output Format

```text
=== REPO PULSE ===
=== TOP RISKS ===
=== QUICK WINS ===
=== SHARP ROAST ===
=== FIX PLAN ===
=== SHARE CARD ===
```

## Training Recipe

- Base model: `JetBrains/Mellum2-12B-A2.5B-Instruct`
- Method: QLoRA with 4-bit NF4 quantization
- Hardware: Modal NVIDIA A10G
- Dataset: synthetic app-format code-review examples
- Sequence length: 2048 tokens

## Limitations

The model reviews bounded uploaded context only. It should not invent file paths,
line numbers, dependency state, or security findings that are not supported by
the supplied repository context.
