# Kerb — 4-Minute Demo Script

Non-technical judges follow the story; technical judges get the reveal at 3:00. Rehearse until the sabotage beat is boring to you — it must feel dangerous to them and safe to you.

## 0:00–0:15 — The hook (start in the deep end)

Screen already on Meridian, dial already on **Autopilot**.

> "This is Meridian, a claims portal. Watch."

Type: *"Issue a refund for claim #4821."* The cursor moves. Fields fill. A reasoning ticker narrates each step. Refund issued in ~12 seconds.

> "No script. No macro. And I'm going to show you why that was actually *safe*."

## 0:15–0:45 — The problem

> "Every company builds this four times: tutorials nobody reads, support docs that go stale the day the UI changes, brittle automations, and QA tests that break weekly. Four teams, four tools — for what is secretly **one artifact**: a validated sequence of steps against a real interface. Kerb builds it once."

## 0:45–2:15 — The dial (same brain, three levels of trust)

Same request, dial on **Guide**:
- The plan compiles visibly: retrieved policy chunks appear with scores, then steps.
- The UI highlights the first control, with *why* + a citation from the refund policy.
- Point out: the plan is different because the refund is over $500 — "the AI read the policy, not the pixels."

Dial to **Copilot**:
- AI proposes each step, presenter confirms, it executes. Fast, collaborative.
- **The gate moment**: one step has low retrieval confidence — Kerb refuses to auto-run it and forces a confirm. "It knows what it doesn't know, per step."

Dial to **Autopilot**:
- Before touching the live app, show the **Runloop dry-run receipt**: the whole plan already ran in a disposable cloud sandbox — screenshots, final state diff. "It rehearsed in a sandbox before it touched anything real."
- Confirm → live replay (this is what judges saw at 0:00, now demystified).

## 2:15–3:00 — THE WOW: sabotage

> "Here's the part every one of these products dreads: the UI changed overnight."

Flip the sabotage switch (env-controlled): the *Approve Refund* button is renamed and moved. Run the guide — it fails, visibly.

> "Normally: stale docs, broken bots, a support ticket. Watch Sentinel."

Trigger Sentinel: replay fails in a Runloop devbox → repair agent diagnoses drift from the DOM snapshot → patches the selector registry → revalidates → re-replays green. Run the guide again on the live app: it works.

> "Our documentation just fixed itself. Nobody filed a ticket. Nobody woke up."

## 3:00–3:40 — Technical reveal (30 seconds, four layers)

> "Four bounded layers, and the LLM is trusted with none of them alone: an **approved selector registry** — the model can only reference logical names, it physically cannot invent a selector; a **server-side validator** — every plan is checked before a single highlight renders; **dual confidence** — retrieval score times model confidence sets the *maximum autonomy per step*; and **Runloop devboxes** — every execution and every nightly replay happens in a sandbox first. UI is pure-Python Reflex — the dial is literally one state variable, which is why all four modes are provably the same engine."

## 3:40–4:00 — Close

> "Tutorials, support, automation, and QA were never four products. They're one plan at four levels of trust. Kerb is the layer that lets any software teach you, help you, or just do it for you — safely."

## Vocabulary guardrails (binding — PostHog AI collision check, report §Review 7b)

- Never say **"session replay"** — on stage Sentinel **"re-runs every guide in a sandbox."**
- The Sentinel screen is the **"verification board"** — never "analytics," "insights," or "dashboard."
- Never pitch "AI that navigates a UI"; pitch the artifact — one compiled, validated plan at four levels of trust.

## Contingency notes

- If Runloop is unreachable on stage: pre-recorded receipt + live everything else; say so honestly, judges forgive infra, not fakery.
- If the model stalls compiling live: plans are cacheable — warm the cache in rehearsal, still compile one live in Guide mode where latency reads as "thinking."
- Sabotage is env-flagged and reversible in one keystroke. Never live-edit code on stage.
