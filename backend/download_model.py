"""Download MiniLM once into backend/model/ (same path semantic_search.default_model_source() uses)."""
from pathlib import Path

from sentence_transformers import SentenceTransformer

OUT = Path(__file__).resolve().parent / "model"

model = SentenceTransformer("all-MiniLM-L6-v2", device="cpu")
model.save(str(OUT))
print(f"Model saved to {OUT}")
