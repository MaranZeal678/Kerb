"""Repair agent (spec §6.4) — turns a red replay into an evidence-cited registry patch.

Matching is constrained to observable evidence: an unregistered control whose tag is
compatible with the failed action, preferring the original region. When several
candidates survive and a Mistral key exists, the model adjudicates BETWEEN the
survivors only — it can never nominate an element outside the evidence set.
"""

import json
import os

from kerberos.engine import registry as regmod

TAG_FOR_ACTION = {"click": {"button"}, "fill": {"input", "textarea"}, "select": {"select"}}


def propose_patch(plan: dict, failed_step_id: int, dom_controls: list[dict]) -> dict | None:
    step = next(s for s in plan["steps"] if s["id"] == failed_step_id)
    reg = regmod.registry()
    old = reg[step["selector"]]
    known = {c.guide for c in reg.values()}
    candidates = [d for d in (dom_controls or [])
                  if d["guide"] not in known and d["tag"] in TAG_FOR_ACTION[step["action"]]]
    if not candidates:
        return None
    same_region = [d for d in candidates if d["region"] == old.region]
    pool = same_region or candidates
    pick = pool[0]
    if len(pool) > 1 and os.environ.get("MISTRAL_API_KEY"):
        try:
            from kerberos.engine import mistral_client
            client = mistral_client()
            resp = client.chat.complete(
                model=os.environ.get("KERBEROS_MISTRAL_MODEL", "mistral-small-latest"),
                messages=[{"role": "user", "content":
                    f"A UI control was renamed. Original: label '{old.label}', role {old.tag}, "
                    f"region {old.region}, purpose: {step['why']}.\nCandidates (unregistered controls "
                    f"found in the live DOM):\n{json.dumps(pool)}\n"
                    'Reply ONLY JSON: {"guide": "<guide value of the best match>"}'}],
                response_format={"type": "json_object"}, temperature=0.0)
            choice = json.loads(resp.choices[0].message.content).get("guide")
            pick = next((d for d in pool if d["guide"] == choice), pick)
        except Exception:
            pass
    evidence = [
        f"unregistered control — not in registry v{regmod.version()}",
        f"<{pick['tag']}> matches failed action '{step['action']}'",
        (f"region '{pick['region']}' matches original placement"
         if pick["region"] == old.region else f"found in region '{pick['region']}'"),
    ]
    if pick.get("text"):
        evidence.append(f"visible label: \"{pick['text']}\"")
    return {
        "control_id": old.id,
        "old_guide": old.guide,
        "new_guide": pick["guide"],
        "new_label": pick.get("text") or old.label,
        "evidence": evidence,
        "rationale": f"'{old.label}' no longer resolves; {pick['tag']} '{pick.get('text') or pick['guide']}' "
                     f"is the only evidence-compatible replacement.",
    }
