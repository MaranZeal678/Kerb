"""Provider-neutral LLM access.

Kerb never imports a vendor SDK. It speaks the standard OpenAI-compatible HTTP
surface (`/chat/completions`, `/embeddings`), so any endpoint implementing that
contract - hosted or self-run - can back the engine by configuration alone:

    KERB_LLM_BASE_URL   e.g. https://<host>/v1
    KERB_LLM_API_KEY
    KERB_LLM_MODEL      chat model id, used by the plan compiler and repair agent
    KERB_EMBED_MODEL    embedding model id, used by retrieval

With no endpoint configured the engine stays fully functional: retrieval falls
back to lexical BM25-style scoring and plan compilation falls back to the
deterministic compiler. The safety layers - registry, validator, grounding
thresholds, sandbox verification - never depend on a model being reachable.
"""

import json
import os

TIMEOUT = 45.0


def _cfg() -> tuple[str, str]:
    base = (os.environ.get("KERB_LLM_BASE_URL") or "").rstrip("/")
    key = os.environ.get("KERB_LLM_API_KEY") or ""
    return base, key


def available() -> bool:
    base, key = _cfg()
    return bool(base and key)


def _post(path: str, payload: dict) -> dict:
    import httpx

    base, key = _cfg()
    if not base or not key:
        raise RuntimeError("no LLM endpoint configured")
    resp = httpx.post(
        f"{base}{path}",
        json=payload,
        headers={"Authorization": f"Bearer {key}", "Content-Type": "application/json"},
        timeout=TIMEOUT,
    )
    resp.raise_for_status()
    return resp.json()


def embed(texts: list[str]) -> list[list[float]]:
    """Embed a batch of strings. Returns one vector per input, input order preserved."""
    model = os.environ.get("KERB_EMBED_MODEL", "")
    data = _post("/embeddings", {"model": model, "input": texts})["data"]
    ordered = sorted(data, key=lambda d: d.get("index", 0))
    return [d["embedding"] for d in ordered]


def chat_json(prompt: str, temperature: float = 0.1) -> dict:
    """Single-turn completion constrained to a JSON object. Returns the parsed object."""
    model = os.environ.get("KERB_LLM_MODEL", "")
    body = _post("/chat/completions", {
        "model": model,
        "messages": [{"role": "user", "content": prompt}],
        "response_format": {"type": "json_object"},
        "temperature": temperature,
    })
    return json.loads(body["choices"][0]["message"]["content"])
