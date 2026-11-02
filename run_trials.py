"""Run Unit 6's three seeds using the starter notebook's training functions."""

import argparse
import ast
import gc
import hashlib
import json
import os
import sys
import time
from pathlib import Path

for stream in (sys.stdout, sys.stderr):
    if hasattr(stream, "reconfigure"):
        stream.reconfigure(encoding="utf-8")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("stage", choices=["before", "after"])
    parser.add_argument("--learning-rate", type=float, default=None)
    args = parser.parse_args()
    root = Path(__file__).resolve().parent
    os.chdir(root)
    os.environ.setdefault("OMP_NUM_THREADS", "4")
    os.environ.setdefault("MKL_NUM_THREADS", "4")
    os.environ.setdefault("HF_HOME", str(root / ".cache" / "huggingface"))

    notebook = json.loads((root / "takemeter.ipynb").read_text(encoding="utf-8"))
    namespace = {}
    # Set up the device, original settings, and data without rerunning Unit 5.
    for index in (2, 6, 8, 10):
        exec("".join(notebook["cells"][index]["source"]), namespace)
    if namespace["problems"]:
        raise ValueError("Fix dataset problems before running trials.")
    # Reuse the exact split/train/evaluate functions, excluding their demo calls.
    for index in (12, 14, 16):
        tree = ast.parse("".join(notebook["cells"][index]["source"]))
        tree.body = [node for node in tree.body if isinstance(
            node, (ast.Import, ast.ImportFrom, ast.FunctionDef)
        )]
        exec(compile(tree, f"notebook_cell_{index}", "exec"), namespace)

    rate = args.learning_rate or namespace["LEARNING_RATE"]
    output = root / f"results_three_seeds_{args.stage}.json"
    if output.exists():
        raise FileExistsError(f"Preserving existing results: {output.name}")
    digest = hashlib.sha256((root / "labels.csv").read_bytes()).hexdigest()
    results = []
    for seed in (42, 7, 2024):
        print(f"\n{args.stage}: seed {seed}, learning rate {rate}", flush=True)
        train, val, test = namespace["split_dataset"](namespace["df"], seed)
        started = time.perf_counter()
        trainer, tokenizer = namespace["train_model"](
            train, val, namespace["LABELS"], seed, namespace["EPOCHS"], rate,
            namespace["BATCH_SIZE"], namespace["BASE_MODEL"], quiet=True,
        )
        result = namespace["evaluate"](trainer, tokenizer, test, namespace["LABELS"], seed)
        result.update({
            "device": namespace["DEVICE"], "device_name": namespace["DEVICE_NAME"],
            "torch_version": namespace["torch"].__version__,
            "base_model": namespace["BASE_MODEL"], "epochs": namespace["EPOCHS"],
            "learning_rate": rate, "batch_size": namespace["BATCH_SIZE"],
            "max_length": namespace["MAX_LENGTH"], "n_train": len(train),
            "n_val": len(val), "labels_sha256": digest,
            "elapsed_seconds": time.perf_counter() - started,
        })
        results.append(result)
        output.write_text(json.dumps(results, indent=2) + "\n", encoding="utf-8")
        print(f"Saved seed {seed}: accuracy {result['accuracy']:.3f}, "
              f"macro F1 {result['f1_macro']:.3f}", flush=True)
        del trainer, tokenizer
        gc.collect()
    print(f"Completed all three seeds: {output.name}", flush=True)


if __name__ == "__main__":
    main()
