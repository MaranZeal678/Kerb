"""Retrieval: chunk policy markdown -> embed (or lexical fallback) -> top-k cosine retrieve.

Grounding inputs: retrieval score (this module) x citation coverage
(also this module — fraction of a step's `why` content-words entailed by its chunk).
Both are computable and deterministic; no uncalibrated model self-assessment anywhere.
"""

import math
import os
import re
from pathlib import Path

from dotenv import load_dotenv

from . import llm

load_dotenv(Path(__file__).parents[2] / ".env")

DOCS_DIR = Path(__file__).parents[2] / "docs" / "policy"
STOP = set(("the a an of to and or is are be been for on in with by from must may might any all this that "
            "these those it its using use used within a's when where which who will shall should can could "
            "before after during into out up down not no if then than as at do does done have has had").split())

_corpus: list[dict] = []      # {doc, chunk, text}
_vectors: list | None = None  # embeddings aligned with _corpus
_mode = "uninitialized"       # embed | lexical


def _tokens(text: str) -> list[str]:
    return [t for t in re.findall(r"[a-z0-9$\.]+", text.lower()) if t not in STOP and len(t) > 1]


def _chunk_markdown(text: str, doc: str) -> list[dict]:
    parts = re.split(r"\n(?=#{1,3} )", text)
    chunks, i = [], 0
    for part in parts:
        part = part.strip()
        if not part:
            continue
        while len(part) > 900:  # split very long sections on paragraph boundaries
            cut = part.rfind("\n\n", 0, 900)
            cut = cut if cut > 200 else 900
            chunks.append({"doc": doc, "chunk": i, "text": part[:cut].strip()}); i += 1
            part = part[cut:].strip()
        chunks.append({"doc": doc, "chunk": i, "text": part}); i += 1
    return chunks


def _ensure() -> None:
    global _corpus, _vectors, _mode
    if _mode != "uninitialized":
        return
    _corpus = []
    for f in sorted(DOCS_DIR.glob("*.md")):
        _corpus.extend(_chunk_markdown(f.read_text(), f.name))
    if llm.available():
        try:
            _vectors = llm.embed([c["text"] for c in _corpus])
            _mode = "embed"
            return
        except Exception:
            pass
    _mode = "lexical"


def _idf(term: str) -> float:
    df = sum(1 for c in _corpus if term in c.get("_tokset", set()))
    return 1.0 + math.log((1 + len(_corpus)) / (1 + df))


def _lexical_scores(query: str) -> list[float]:
    for c in _corpus:
        c.setdefault("_tokset", set(_tokens(c["text"])))
    q = set(_tokens(query))
    if not q:
        return [0.0] * len(_corpus)
    total = sum(_idf(t) for t in q)
    return [sum(_idf(t) for t in q if t in c["_tokset"]) / total for c in _corpus]


def retrieve(query: str, k: int = 4) -> list[dict]:
    _ensure()
    if _mode == "embed":
        try:
            qv = llm.embed([query])[0]
            def cos(a, b):
                dot = sum(x * y for x, y in zip(a, b))
                na = math.sqrt(sum(x * x for x in a)); nb = math.sqrt(sum(x * x for x in b))
                return dot / (na * nb) if na and nb else 0.0
            scores = [cos(qv, v) for v in _vectors]
        except Exception:
            scores = _lexical_scores(query)
    else:
        scores = _lexical_scores(query)
    ranked = sorted(zip(_corpus, scores), key=lambda p: -p[1])[:k]
    return [{"doc": c["doc"], "chunk": c["chunk"], "text": c["text"], "score": round(s, 3)}
            for c, s in ranked]


def coverage(why: str, chunk_text: str) -> float:
    """Fraction of the step's claim content-words supported by the cited chunk."""
    w = _tokens(why)
    if not w:
        return 0.0
    chunk = set(_tokens(chunk_text))
    return round(sum(1 for t in w if t in chunk) / len(w), 3)


def docs_version() -> str:
    _ensure()
    stamp = sum(int(f.stat().st_mtime) for f in DOCS_DIR.glob("*.md"))
    return f"d{stamp % 100000}"


def mode() -> str:
    _ensure()
    return _mode
