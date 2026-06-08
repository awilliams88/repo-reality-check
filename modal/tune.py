from __future__ import annotations

import os
from typing import Any

import modal

modal_any: Any = modal

# Modal app groups the remote fine-tuning job.
app = modal_any.App("repo-reality-check-tuner")

# Container includes review SFT dependencies and local dataset code.
image = (
    modal_any.Image.debian_slim()
    .pip_install(
        "torch",
        "transformers>=4.45.0",
        "peft",
        "trl",
        "accelerate",
        "bitsandbytes",
        "datasets",
        "huggingface_hub",
    )
    .add_local_file(
        os.path.join(os.path.dirname(__file__), "dataset.py"),
        "/root/dataset.py",
    )
)

volume = modal_any.Volume.from_name(
    "repo-reality-check-checkpoints", create_if_missing=True
)

MODEL_ID = "JetBrains/Mellum2-12B-A2.5B-Instruct"
ADAPTER_REPO_ID = "build-small-hackathon/repo-reality-check-review-lora"


@app.function(
    image=image,
    gpu="A10G",
    timeout=7200,
    volumes={"/checkpoints": volume},
    secrets=[modal_any.Secret.from_name("huggingface-secret")],
)
def train_lora(model_card_content: str, hf_token: str | None = None):
    """Fine-tunes a compact code-review adapter on the production review format."""
    # Remote-only imports are installed inside the Modal container.
    import io
    import os as remote_os

    import torch
    from datasets import Dataset
    from huggingface_hub import login, upload_file
    from peft import LoraConfig, get_peft_model, prepare_model_for_kbit_training
    from transformers import AutoModelForCausalLM, AutoTokenizer, BitsAndBytesConfig
    from trl import SFTConfig, SFTTrainer

    from dataset import build_training_prompt, get_training_examples

    # Format examples in the current UI section format.
    tokenizer = AutoTokenizer.from_pretrained(MODEL_ID, trust_remote_code=True)
    rows = []
    for item in get_training_examples():
        messages = [
            {
                "role": "user",
                "content": build_training_prompt(str(item["repo"]), str(item["notes"])),
            },
            {"role": "assistant", "content": str(item["response"])},
        ]
        rows.append({"text": tokenizer.apply_chat_template(messages, tokenize=False)})
    dataset = Dataset.from_list(rows)
    print(f"Prepared {len(dataset)} repo-review conversations.")

    # QLoRA keeps training feasible on a single Modal A10G.
    bnb_config = BitsAndBytesConfig(
        load_in_4bit=True,
        bnb_4bit_quant_type="nf4",
        bnb_4bit_compute_dtype=torch.bfloat16,
        bnb_4bit_use_double_quant=True,
    )
    model = AutoModelForCausalLM.from_pretrained(
        MODEL_ID,
        quantization_config=bnb_config,
        device_map="auto",
        trust_remote_code=True,
    )
    model.config.pad_token_id = tokenizer.eos_token_id
    model = prepare_model_for_kbit_training(model)
    model = get_peft_model(
        model,
        LoraConfig(
            r=16,
            lora_alpha=32,
            target_modules=["q_proj", "v_proj", "k_proj", "o_proj"],
            lora_dropout=0.05,
            bias="none",
            task_type="CAUSAL_LM",
        ),
    )
    args = SFTConfig(
        output_dir="/checkpoints/repo-reality-check-lora",
        per_device_train_batch_size=1,
        gradient_accumulation_steps=4,
        warmup_steps=8,
        max_steps=180,
        learning_rate=2e-4,
        bf16=True,
        logging_steps=5,
        save_strategy="steps",
        save_steps=45,
        save_total_limit=2,
        report_to="none",
        dataset_text_field="text",
        max_length=2048,
    )
    trainer = SFTTrainer(model=model, train_dataset=dataset, args=args)
    trainer.train()
    model.save_pretrained("/checkpoints/repo-reality-check-final")
    tokenizer.save_pretrained("/checkpoints/repo-reality-check-final")
    volume.commit()

    # Publish the adapter and model card when credentials are available.
    hf_token = hf_token or remote_os.environ.get("HF_TOKEN")
    if hf_token:
        login(token=hf_token)
        model.push_to_hub(ADAPTER_REPO_ID)
        tokenizer.push_to_hub(ADAPTER_REPO_ID)
        upload_file(
            path_or_fileobj=io.BytesIO(model_card_content.encode("utf-8")),
            path_in_repo="README.md",
            repo_id=ADAPTER_REPO_ID,
            repo_type="model",
            commit_message="Update Repo Reality Check adapter model card",
        )
    else:
        print("HF_TOKEN not set. Skipping Hub publish.")


@app.local_entrypoint()
def main():
    # Read CARD.md dynamically so latest metadata is included in the run.
    meta_path = os.path.join(os.path.dirname(__file__), "CARD.md")
    with open(meta_path, encoding="utf-8") as f:
        model_card = f.read()
    train_lora.remote(model_card_content=model_card)
