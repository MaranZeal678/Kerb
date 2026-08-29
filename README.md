# Kerberos

**One guidance engine. Four levels of trust. Software that can teach you, help you, act for you — and heal itself when the UI changes.**

Kerberos is named for the three-headed watchdog: three heads, one body. The product is exactly that — **one underlying AI plan engine** projected at three autonomy levels the user can toggle between, plus a fourth headless mode that guards all the others.

## The core insight

Tutorials, in-app support, RPA-style automation, and UI regression tests are treated as four different products built by four different teams. They are actually **the same artifact**: a grounded, validated sequence of steps against a real interface. Kerberos builds that artifact once — a **Guide Plan** — and projects it at four trust levels:

| Mode | Projection of the same plan | Who it serves |
|---|---|---|
| 🐕 **Guide** | Rendered as visual walkthrough: highlights, pointers, doc citations | New users learning the flow |
| 🐕 **Copilot** | Executed step-by-step, human confirms each action | Everyday users doing it faster |
| 🐕 **Autopilot** | Dry-run in a Runloop sandbox, then executed end-to-end with a receipt | Power users who just want it done |
| 👁 **Sentinel** | Replayed continuously in Runloop devboxes against the app; failures trigger a self-healing repair loop | Nobody — it runs while everyone sleeps |

The mode toggle is not a feature switcher. It is an **autonomy dial** over one engine — which is what makes it a real platform demo instead of four apps behind tabs.

## Why this is not a chatbot

- The AI never free-texts instructions. It **compiles plans against an approved selector registry** (`data-guide` attributes), and every plan is validated server-side before a single highlight renders. An unapproved selector is a compile error, not a hallucination the user has to catch.
- Answers are grounded by RAG over the operational policy docs, and **dual confidence (retrieval score × model confidence) gates the maximum allowed autonomy per step**. A low-confidence step can render as a highlight but can never auto-execute.
- Autopilot never touches the live UI first. Every execution **dry-runs in a disposable Runloop devbox**, producing an execution receipt (screenshots + state diff) before replay on the real interface.
- Sentinel makes the guides **self-testing and self-healing**: when the UI drifts (a button renamed, a field moved), replays fail in the sandbox, a repair agent patches the selector registry and plan, revalidates, and the fix ships — before a human ever hits the broken guide.

## Demo scenario

**Meridian** — a realistic mock claims/refund back-office portal built into this repo and instrumented with the selector registry. The demo task: *"Issue a refund for claim #4821."* Policy docs (RAG) require different steps above a $500 threshold, so the plan visibly depends on grounded knowledge, not UI guessing.

The wow moment: we **sabotage Meridian's UI live on stage**, watch Sentinel catch the break in a Runloop sandbox, and watch the guide repair itself.

## Stack

- **Reflex** — the entire platform and the Meridian demo app, pure Python. Websocket-driven state is what makes real-time step streaming, live highlights, and the mode toggle feel instant.
- **Mistral** — chat models for plan compilation and repair reasoning; embeddings for the RAG pipeline.
- **Runloop** — disposable devboxes for Autopilot dry-runs, continuous Sentinel replay, and scoring guide reliability over time.
- **Playwright** (inside devboxes) — headless execution of Guide Plans.

## Repository layout

```
kerberos/            Reflex app: platform shell, mode toggle, overlay
  engine/            Plan compiler, selector registry, server-side validator, RAG
  meridian/          The instrumented demo app (mock claims portal)
sentinel/            Runloop replay runner + self-heal repair agent
docs/                Architecture, roadmap, demo script, concept evaluation
```

## Documents

- **[KERBEROS_ELITE_PRODUCT_EVALUATION_REPORT.md](KERBEROS_ELITE_PRODUCT_EVALUATION_REPORT.md) — the gstack elite evaluation and final spec. Where it conflicts with the docs below, the report wins.**
- [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md) — full system design with diagrams
- [docs/ROADMAP.md](docs/ROADMAP.md) — tiered build plan with estimates
- [docs/DEMO_SCRIPT.md](docs/DEMO_SCRIPT.md) — the 4-minute demo, timed
- [docs/CONCEPT_EVALUATION.md](docs/CONCEPT_EVALUATION.md) — the 10 concepts considered and why this one won

## Status

Planning + scaffold committed. Implementation follows the roadmap tiers (Tier 1 = Meridian app, selector registry, plan compiler, Guide/Copilot modes). Scaffold code is structural and not yet run end-to-end.
