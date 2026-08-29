"""RAG pipeline: chunk markdown policy docs -> Mistral embeddings -> in-memory store -> cosine top-k.

Each retrieval carries its score into the plan; grounding_score per step =
f(retrieval score, citation coverage). Below-threshold goals escalate to a
human-handoff card instead of producing a plan.

STATUS: scaffold. Implement in Tier 1.3 (port of the proven chunk/embed/retrieve design).
"""


def ingest(doc_path: str) -> int:
    """Chunk + embed one markdown doc; returns chunk count. Replaces prior version of the same doc."""
    raise NotImplementedError("Tier 1.3")


def retrieve(query: str, k: int = 4) -> list[dict]:
    """Return [{doc, chunk, text, score}] sorted by cosine similarity."""
    raise NotImplementedError("Tier 1.3")
