"""
Semantic search over UA resources using sentence embeddings.
Corpus embeddings are precomputed (embeddings.npy) and reused; only the query is encoded per request.

Deployed Link: https://ua-semantic-search.vercel.app/
It takes 2-5 seconds to search for a resource since a free trial version of gcloud is used.
"""

from __future__ import annotations

import logging
import re
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Sequence

import numpy as np
import pandas as pd
from sentence_transformers import SentenceTransformer

logger = logging.getLogger(__name__)

# -----------------------------------------------------------------------------
# Paths (resolve relative to this file so imports work from any cwd)
# -----------------------------------------------------------------------------
_BACKEND_DIR = Path(__file__).resolve().parent
DEFAULT_DATA_PATH = _BACKEND_DIR / "ua_resources_filled.xlsx"
FALLBACK_DATA_PATH = _BACKEND_DIR / "ua_resources.xlsx"
DEFAULT_EMBEDDINGS_PATH = _BACKEND_DIR / "embeddings.npy"
DEFAULT_MODEL_PATH = _BACKEND_DIR / "model"


# -----------------------------------------------------------------------------
# Query expansion (keyword → extra phrases). Easy to extend: add tuples.
# -----------------------------------------------------------------------------
_EXPANSION_RULES: tuple[tuple[tuple[str, ...], tuple[str, ...]], ...] = (
    (("grade",), ("check grades blackboard assignments",)),
    (("class", "course"), ("schedule classes degreeworks",)),
    (("email", "contact"), ("email professor faculty directory",)),
    (("scholarship",), ("apply scholarships financial aid",)),
)


def _dedupe_consecutive_tokens(text: str) -> str:
    """Collapse immediate token repetition (e.g. 'help help' → 'help')."""
    parts = text.split()
    if not parts:
        return ""
    out = [parts[0]]
    for w in parts[1:]:
        if w != out[-1]:
            out.append(w)
    return " ".join(out)


def _normalize_whitespace(text: str) -> str:
    return re.sub(r"\s+", " ", text.strip())


def expand_query(query: str) -> str:
    """Add domain phrases for common student intents; keeps rules data-driven."""
    q = _normalize_whitespace(str(query).lower())
    if not q:
        return ""
    extras: list[str] = []
    for keywords, snippets in _EXPANSION_RULES:
        if any(k in q for k in keywords):
            extras.extend(snippets)
    if not extras:
        return q
    merged = f"{q} {' '.join(extras)}"
    return _dedupe_consecutive_tokens(_normalize_whitespace(merged))


def build_search_text_column(df: pd.DataFrame) -> pd.Series:
    """
    Same weighting as fill_dataset.py: name and student_queries emphasized.
    Stored lowercase for consistent retrieval.
    """
    name = df["resource_name"].fillna("").astype(str).str.strip()
    sq = df["student_queries"].fillna("").astype(str).str.strip()
    desc = df["description"].fillna("").astype(str).str.strip()
    kw = df["keywords"].fillna("").astype(str).str.strip()
    cat = df["category"].fillna("").astype(str).str.strip()
    sub = df["subcategory"].fillna("").astype(str).str.strip()

    combined = (
        (name + " ") * 3
        + (sq + " ") * 2
        + desc
        + " "
        + kw
        + " "
        + cat
        + " "
        + sub
    )
    out = combined.str.lower().map(_normalize_whitespace).map(_dedupe_consecutive_tokens)
    return out


def clean_data(df: pd.DataFrame) -> pd.DataFrame:
    """
    Dedupe, fill missing text fields, normalize taxonomy, rebuild search_text.
    Drops rows with no usable name or empty search_text after cleaning.
    """
    out = df.copy()
    if "resource_name" not in out.columns:
        out["resource_name"] = ""
    for col in ("description", "keywords", "student_queries", "url", "category"):
        if col not in out.columns:
            out[col] = ""
    if "subcategory" not in out.columns:
        out["subcategory"] = "Unknown"
    out["resource_name"] = out["resource_name"].fillna("").astype(str).str.strip()
    out["category"] = out["category"].fillna("").astype(str).str.strip().str.lower()
    out["subcategory"] = out["subcategory"].fillna("Unknown").astype(str).str.strip().str.lower()

    for col in ("description", "keywords", "student_queries", "url"):
        if col in out.columns:
            out[col] = out[col].fillna("").astype(str).str.strip()

    # Duplicate resources: keep first stable row
    key = out["resource_name"].str.lower()
    out = out.assign(_rn=key).drop_duplicates(subset=["_rn"], keep="first").drop(columns=["_rn"])

    out["search_text"] = build_search_text_column(out)
    # Near-duplicate documents (identical retrieval surface)
    out = out.drop_duplicates(subset=["search_text"], keep="first")

    out = out[out["resource_name"].str.len() > 0]
    out = out[out["search_text"].str.len() > 0]
    return out.reset_index(drop=True)


def load_resources(
    data_path: Path | str | None = None,
) -> pd.DataFrame:
    """Load spreadsheet; prefer enriched file, fallback to raw."""
    path = Path(data_path) if data_path else DEFAULT_DATA_PATH
    if not path.exists():
        path = FALLBACK_DATA_PATH
    if not path.exists():
        raise FileNotFoundError(f"No dataset found at {DEFAULT_DATA_PATH} or {FALLBACK_DATA_PATH}")
    df = pd.read_excel(path)
    logger.info("Loaded dataset: %s (%s rows)", path.name, len(df))
    return clean_data(df)


def default_model_source() -> str:
    """Prefer local `backend/model/` (Docker build / download_model); else Hugging Face id."""
    if DEFAULT_MODEL_PATH.is_dir():
        return str(DEFAULT_MODEL_PATH)
    return "all-MiniLM-L6-v2"


def _normalize_embedding_matrix(emb: np.ndarray) -> np.ndarray:
    norms = np.linalg.norm(emb, axis=1, keepdims=True)
    norms = np.where(norms == 0, 1.0, norms)
    return emb / norms


@dataclass
class SearchResult:
    name: str
    description: str
    url: str
    score: float


class SearchEngine:
    """
    Holds model + corpus embeddings + dataframe once. Thread-safe for concurrent encode() calls.
    """

    def __init__(
        self,
        data_path: Path | str | None = None,
        embeddings_path: Path | str | None = None,
        model_source: str | None = None,
    ) -> None:
        self.data_path = Path(data_path) if data_path else DEFAULT_DATA_PATH
        self.embeddings_path = Path(embeddings_path) if embeddings_path else DEFAULT_EMBEDDINGS_PATH
        self.model_source = model_source or default_model_source()

        self._df: pd.DataFrame | None = None
        self._embeddings: np.ndarray | None = None
        self._model: SentenceTransformer | None = None
        self._loaded = False

    def _ensure_model(self) -> SentenceTransformer:
        if self._model is None:
            logger.info("Loading sentence-transformer model from %s", self.model_source)
            self._model = SentenceTransformer(self.model_source, device="cpu")
        return self._model

    def _build_corpus_embeddings(self, model: SentenceTransformer) -> np.ndarray:
        assert self._df is not None
        texts = self._df["search_text"].tolist()
        logger.info("Encoding corpus (%d documents) — one-time cost if cache mismatch", len(texts))
        emb = model.encode(
            texts,
            batch_size=64,
            show_progress_bar=False,
            normalize_embeddings=True,
            convert_to_numpy=True,
        )
        return np.asarray(emb, dtype=np.float32)

    def _load_or_build_embeddings(self, model: SentenceTransformer) -> np.ndarray:
        assert self._df is not None
        n = len(self._df)

        if self.embeddings_path.exists():
            emb = np.load(self.embeddings_path)
            if emb.shape[0] == n and emb.ndim == 2:
                emb = _normalize_embedding_matrix(np.asarray(emb, dtype=np.float32))
                logger.info("Loaded corpus embeddings from %s", self.embeddings_path.name)
                return emb

        logger.warning(
            "Embeddings missing or row count mismatch (file=%s, need %d rows). Re-encoding corpus.",
            self.embeddings_path.name,
            n,
        )
        return self._build_corpus_embeddings(model)

    def load(self) -> None:
        if self._loaded:
            return
        self._df = load_resources(self.data_path)
        model = self._ensure_model()
        self._embeddings = self._load_or_build_embeddings(model)
        self._loaded = True
        logger.info("SearchEngine ready (%d resources)", len(self._df))

    @property
    def df(self) -> pd.DataFrame:
        if self._df is None:
            raise RuntimeError("Call load() before accessing df")
        return self._df

    def search(
        self,
        query: str,
        *,
        top_k: int = 5,
        expand: bool = True,
        min_score: float | None = None,
    ) -> list[SearchResult]:
        """Return top_k results by cosine similarity (embeddings are L2-normalized)."""
        self.load()
        assert self._df is not None and self._embeddings is not None and self._model is not None

        q_raw = expand_query(query) if expand else _normalize_whitespace(str(query).lower())
        if not q_raw:
            return []

        q_emb = self._model.encode(
            [q_raw],
            normalize_embeddings=True,
            convert_to_numpy=True,
        )
        q_emb = np.asarray(q_emb, dtype=np.float32)
        # Cosine similarity == dot product when both are unit vectors
        scores = (self._embeddings @ q_emb.T).ravel()

        k = min(top_k, len(scores))
        if k < 1:
            return []

        # argpartition avoids full sort (minor gain; keeps code simple for large n)
        if k >= len(scores):
            top_idx = np.argsort(scores)[::-1][:k]
        else:
            part = np.argpartition(scores, -k)[-k:]
            top_idx = part[np.argsort(scores[part])][::-1]

        results: list[SearchResult] = []
        for idx in top_idx:
            s = float(scores[idx])
            if min_score is not None and s < min_score:
                continue
            row = self._df.iloc[int(idx)]
            results.append(
                SearchResult(
                    name=str(row["resource_name"]),
                    description=str(row.get("description", "")),
                    url=str(row.get("url", "")),
                    score=s,
                )
            )
        return results

    def search_dict(self, query: str, **kwargs: Any) -> dict[str, Any]:
        """API-friendly payload."""
        rows = self.search(query, **kwargs)
        return {
            "results": [
                {"name": r.name, "description": r.description, "url": r.url, "score": r.score}
                for r in rows
            ]
        }


_engine: SearchEngine | None = None


def get_search_engine(
    data_path: Path | str | None = None,
    embeddings_path: Path | str | None = None,
    model_source: str | None = None,
) -> SearchEngine:
    """Process-wide singleton so the model and corpus load once per app lifetime."""
    global _engine
    if _engine is None:
        _engine = SearchEngine(
            data_path=data_path,
            embeddings_path=embeddings_path,
            model_source=model_source,
        )
        _engine.load()
    return _engine


def main(argv: Sequence[str] | None = None) -> None:
    logging.basicConfig(level=logging.INFO, format="%(levelname)s %(message)s")
    engine = get_search_engine()
    print("\nSemantic search ready. Type 'exit' to quit.\n")

    while True:
        try:
            user_input = input("Enter your question: ").strip()
        except (EOFError, KeyboardInterrupt):
            print()
            break

        if user_input.lower() == "exit":
            break
        if not user_input:
            continue

        for r in engine.search(user_input):
            print(f"- {r.name}")
            print(f"  {r.description}")
            print(f"  Link: {r.url}")
            print(f"  Score: {r.score:.4f}\n")
        print("-" * 50)


if __name__ == "__main__":
    main(sys.argv[1:])
