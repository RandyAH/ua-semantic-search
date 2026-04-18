"""
Regenerate backend/embeddings.npy after changing the spreadsheet or clean_data() logic.
Run from repo root:  python scripts/generate_embeddings.py
"""
from __future__ import annotations

import sys
from pathlib import Path

import numpy as np
from sentence_transformers import SentenceTransformer

BACKEND = Path(__file__).resolve().parent.parent / "backend"
sys.path.insert(0, str(BACKEND))

from semantic_search import load_resources, default_model_source  # noqa: E402

OUTPUT_PATH = BACKEND / "embeddings.npy"


def main() -> None:
    df = load_resources(BACKEND / "ua_resources_filled.xlsx")
    model = SentenceTransformer(default_model_source(), device="cpu")
    texts = df["search_text"].tolist()
    print(f"Encoding {len(texts)} documents...")
    embeddings = model.encode(
        texts,
        batch_size=64,
        show_progress_bar=True,
        normalize_embeddings=True,
    )
    np.save(OUTPUT_PATH, embeddings)
    print(f"Saved {OUTPUT_PATH} (shape={embeddings.shape})")


if __name__ == "__main__":
    main()
