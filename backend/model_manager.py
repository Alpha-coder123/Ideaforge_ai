"""
ModelManager — Handles HuggingFace model loading & text generation.

Supported lightweight models (good for local CPU/GPU):
  - google/flan-t5-base              (~250MB, ~1GB RAM)  ← default / fastest
  - google/flan-t5-large             (~780MB, ~2GB RAM)
  - google/flan-t5-xl                (~3GB,   ~5GB RAM)
  - TinyLlama/TinyLlama-1.1B-Chat-v1.0  (~2.2GB, ~3GB RAM)
  - microsoft/phi-2                  (~5.5GB, ~6GB RAM)
  - mistralai/Mistral-7B-Instruct-v0.1  (needs 16GB RAM / GPU)
  - Qwen/Qwen2-0.5B-Instruct         (~1GB,  ~2GB RAM, fast & decent)
  - Qwen/Qwen2-1.5B-Instruct         (~3GB,  ~4GB RAM)
"""

import torch
import logging
from transformers import (
    AutoTokenizer,
    AutoModelForCausalLM,
    AutoModelForSeq2SeqLM,
    pipeline,
)

logger = logging.getLogger(__name__)

# Models that use encoder-decoder (seq2seq) architecture
SEQ2SEQ_MODELS = {"flan-t5", "t5", "bart", "pegasus", "mt5"}


class ModelManager:
    def __init__(self):
        self.model = None
        self.tokenizer = None
        self.pipe = None
        self.model_name = None
        self.device = "cpu"
        self._loaded = False

    def is_loaded(self) -> bool:
        return self._loaded

    def _is_seq2seq(self, model_name: str) -> bool:
        name_lower = model_name.lower()
        return any(key in name_lower for key in SEQ2SEQ_MODELS)

    def unload(self):
        """Free memory before loading a new model."""
        if self.pipe is not None:
            del self.pipe
            self.pipe = None
        if self.model is not None:
            del self.model
            self.model = None
        if self.tokenizer is not None:
            del self.tokenizer
            self.tokenizer = None
        self._loaded = False

        # Free GPU / MPS memory
        if torch.cuda.is_available():
            torch.cuda.empty_cache()
        try:
            if torch.backends.mps.is_available():
                torch.mps.empty_cache()
        except Exception:
            pass

        logger.info("Previous model unloaded and memory freed.")

    def load(self, model_name: str = "google/flan-t5-base"):
        """Load model and tokenizer from HuggingFace Hub."""
        logger.info(f"Loading model: {model_name}")

        # Unload any previously loaded model first
        self.unload()

        # ── Device detection ────────────────────────────────────────────────
        if torch.cuda.is_available():
            self.device = "cuda"
            logger.info("GPU detected — using CUDA")
        elif torch.backends.mps.is_available():
            # MPS (Apple Silicon) works for inference but has quirks;
            # use CPU for stability unless user explicitly wants MPS.
            self.device = "cpu"
            logger.info("Apple Silicon detected — using CPU for stability (MPS has pipeline issues)")
        else:
            self.device = "cpu"
            logger.info("No GPU detected — using CPU")

        self.model_name = model_name
        is_seq2seq = self._is_seq2seq(model_name)

        try:
            self.tokenizer = AutoTokenizer.from_pretrained(
                model_name,
                use_fast=True,
                trust_remote_code=True,
            )

            # Add pad token if missing (common in causal LMs)
            if self.tokenizer.pad_token is None:
                self.tokenizer.pad_token = self.tokenizer.eos_token

            dtype = torch.float32 if self.device == "cpu" else torch.float16

            if is_seq2seq:
                self.model = AutoModelForSeq2SeqLM.from_pretrained(
                    model_name,
                    torch_dtype=dtype,
                    trust_remote_code=True,
                )
                task = "text2text-generation"
            else:
                load_kwargs = {
                    "torch_dtype": dtype,
                    "trust_remote_code": True,
                    "low_cpu_mem_usage": True,
                }
                if self.device == "cuda":
                    load_kwargs["device_map"] = "auto"

                self.model = AutoModelForCausalLM.from_pretrained(
                    model_name,
                    **load_kwargs
                )
                task = "text-generation"

            # Move to device manually (CPU or MPS; CUDA uses device_map)
            if self.device in ("cpu",):
                self.model = self.model.to(self.device)

            self.model.eval()  # inference mode

            # ── Pipeline ────────────────────────────────────────────────────
            # IMPORTANT: For pipeline device argument:
            #   - CUDA  → device=0 (or device_map handled above)
            #   - CPU   → device=-1  (NOT "cpu" string — older transformers need int)
            pipe_device = 0 if self.device == "cuda" else -1

            self.pipe = pipeline(
                task,
                model=self.model,
                tokenizer=self.tokenizer,
                device=pipe_device,
                # Generation quality
                do_sample=True,
                temperature=0.8,
                top_p=0.92,
                top_k=50,
                repetition_penalty=1.3,
                no_repeat_ngram_size=3,
                early_stopping=False,
            )

            self._loaded = True
            logger.info(f"✅ Model '{model_name}' loaded on {self.device}")

        except Exception as e:
            self._loaded = False
            logger.error(f"❌ Failed to load model: {e}")
            raise

    def generate(self, prompt: str, max_new_tokens: int = 400) -> str:
        """Generate text from a prompt."""
        if not self._loaded:
            raise RuntimeError("Model not loaded. Call load() first.")

        try:
            is_seq2seq = self._is_seq2seq(self.model_name)

            if is_seq2seq:
                results = self.pipe(
                    prompt,
                    max_new_tokens=max_new_tokens,
                    min_new_tokens=60,
                )
                text = results[0]["generated_text"]
            else:
                results = self.pipe(
                    prompt,
                    max_new_tokens=max_new_tokens,
                    min_new_tokens=60,
                    return_full_text=False,
                    pad_token_id=self.tokenizer.eos_token_id,
                )
                text = results[0]["generated_text"]

            return text.strip()

        except Exception as e:
            logger.error(f"Generation error: {e}")
            return f"[Generation error: {str(e)}]"
