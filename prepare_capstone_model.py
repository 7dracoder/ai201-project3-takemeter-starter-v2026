"""Rebuild the already-tested Unit 6 seed-42 checkpoint, preserving old results."""

import ast
import hashlib
import json
import os
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent
REVISION = "12040accade4e8a0f71eabdb258fecc2e7e948be"


def main():
    os.chdir(ROOT)
    os.environ.setdefault("OMP_NUM_THREADS", "4")
    os.environ.setdefault("MKL_NUM_THREADS", "4")
    os.environ.setdefault("HF_HOME", str(ROOT / ".cache" / "huggingface"))
    digest = hashlib.sha256((ROOT / "labels.csv").read_bytes()).hexdigest()
    output = ROOT / "models" / "capstone"
    if (output / "manifest.json").exists():
        manifest = json.loads((output / "manifest.json").read_text())
        if manifest["labels_sha256"] != digest or not (output / "model.safetensors").exists():
            raise ValueError("Existing model does not match the dataset; preserve it and investigate.")
        print("Existing capstone checkpoint is ready.")
        return

    notebook = json.loads((ROOT / "takemeter.ipynb").read_text(encoding="utf-8"))
    namespace = {}
    for index in (2, 6, 8, 10):
        exec("".join(notebook["cells"][index]["source"]), namespace)
    if namespace["problems"]:
        raise ValueError("Dataset checks failed.")
    for index in (12, 14, 16):
        tree = ast.parse("".join(notebook["cells"][index]["source"]))
        tree.body = [node for node in tree.body if isinstance(
            node, (ast.Import, ast.ImportFrom, ast.FunctionDef)
        )]
        exec(compile(tree, f"notebook_cell_{index}", "exec"), namespace)
    from huggingface_hub import snapshot_download
    snapshot = snapshot_download(
        "distilbert-base-uncased", revision=REVISION,
        allow_patterns=["config.json", "tokenizer_config.json", "tokenizer.json",
                        "vocab.txt", "model.safetensors"],
    )
    train, val, test = namespace["split_dataset"](namespace["df"], 42)
    trainer, tokenizer = namespace["train_model"](
        train, val, namespace["LABELS"], 42, 3, 5e-5, 16, snapshot, quiet=True
    )
    result = namespace["evaluate"](trainer, tokenizer, test, namespace["LABELS"], 42)
    trainer.save_model(str(output))
    tokenizer.save_pretrained(str(output))
    weights = output / "model.safetensors"
    manifest = {
        "created_at": datetime.now(timezone.utc).isoformat(),
        "base_model": "distilbert-base-uncased", "revision": REVISION,
        "seed": 42, "epochs": 3, "learning_rate": 5e-5,
        "batch_size": 16, "max_length": 128, "labels_sha256": digest,
        "weights_bytes": weights.stat().st_size,
        "weights_sha256": hashlib.sha256(weights.read_bytes()).hexdigest(),
        "regression_result": result,
    }
    (output / "manifest.json").write_text(json.dumps(manifest, indent=2) + "\n")
    print("Saved models/capstone; original Unit 5/6 results were not modified.")


if __name__ == "__main__":
    main()
