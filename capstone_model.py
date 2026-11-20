"""Serve the existing Unit 6 classifier without changing its taxonomy."""

from pathlib import Path

import torch
from transformers import AutoModelForSequenceClassification, AutoTokenizer


class Predictor:
    def __init__(self, model_dir):
        self.model_dir = Path(model_dir)
        if not (self.model_dir / "model.safetensors").is_file():
            raise FileNotFoundError("Run prepare_capstone_model.py first.")
        torch.set_num_threads(4)
        self.load_count = 0
        self._tokenizer = None
        self._model = None

    def predict(self, text):
        # One operational improvement: reuse immutable inference assets.
        if self._model is None:
            self._tokenizer = AutoTokenizer.from_pretrained(self.model_dir, local_files_only=True)
            self._model = AutoModelForSequenceClassification.from_pretrained(
                self.model_dir, local_files_only=True
            ).eval()
            self.load_count += 1
        tokenizer, model = self._tokenizer, self._model
        inputs = tokenizer(text, return_tensors="pt", truncation=True, max_length=128)
        with torch.inference_mode():
            scores = model(**inputs).logits.softmax(dim=-1)[0]
        index = int(scores.argmax())
        return {"label": model.config.id2label[index], "confidence": float(scores[index])}
