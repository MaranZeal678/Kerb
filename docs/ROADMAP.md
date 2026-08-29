# Kerberos Build Roadmap

Estimates assume 2 focused builders. Demo impact is judged against the 4-minute script in [DEMO_SCRIPT.md](DEMO_SCRIPT.md).

## Tier 1 — Must build (the demo dies without these)

| # | Feature | Difficulty | Est. | Depends on | Demo impact |
|---|---|---|---|---|---|
| 1.1 | Meridian demo app in Reflex (claims list, claim detail, refund flow, ~12 instrumented controls) | Medium | 4–5 h | — | Critical — it's the stage |
| 1.2 | Selector registry + server-side validator | Low | 2 h | 1.1 | Critical — the safety story |
| 1.3 | RAG pipeline over 3–4 policy docs (Mistral embeddings, in-memory store) | Medium | 3 h | — | High — grounds every plan |
| 1.4 | Plan compiler (Mistral chat, JSON-constrained, confidence fields) | Medium | 3 h | 1.2, 1.3 | Critical |
| 1.5 | Guide mode: overlay, highlight, pointer, step card with citations | Medium | 4 h | 1.1, 1.4 | Critical — first visual proof |
| 1.6 | Copilot mode: step proposal + confirm-to-execute via shared state | Medium | 3 h | 1.5 | High |
| 1.7 | Autonomy dial UI (the toggle itself — make it gorgeous) | Low | 2 h | 1.5, 1.6 | Critical — it's the thesis |

**Tier 1 total: ~21 h.** At the end of Tier 1 the demo already beats most RAG projects: grounded plans, visual guidance, two autonomy levels, real safety architecture.

## Tier 2 — High impact (this is where it wins)

| # | Feature | Difficulty | Est. | Depends on | Demo impact |
|---|---|---|---|---|---|
| 2.1 | Autopilot: plan execution engine with reasoning ticker (live UI) | Medium | 3 h | 1.6 | Very high — the crowd-pleaser |
| 2.2 | Runloop dry-run: devbox launch, Playwright replay, execution receipt | High | 5 h | 2.1 | Very high — technical credibility |
| 2.3 | Confidence gating: per-step max autonomy, forced-confirm demo moment | Medium | 2 h | 1.4, 2.1 | High — the judges' "safe autonomy" checkbox |
| 2.4 | Sentinel replay loop: run all plans in devboxes, red/green board | Medium | 3 h | 2.2 | High |
| 2.5 | **Self-heal: drift detection → repair agent → registry patch → green** | High | 5 h | 2.4 | **The wow moment. Non-negotiable if time exists.** |

**Tier 2 total: ~18 h.** 2.5 is the memory the judges leave with; protect time for it.

## Tier 3 — Stretch (only after everything above is polished)

| # | Feature | Difficulty | Est. | Depends on | Demo impact |
|---|---|---|---|---|---|
| 3.1 | Escalation flow: low-confidence goal → human handoff card with partial plan | Low | 2 h | 2.3 | Medium |
| 3.2 | ~~Guide analytics~~ CUT per evaluation report (PostHog-collision + pruning): only a single per-plan success stat on the Sentinel verification board survives | — | — | — | — |
| 3.3 | Second target app (tiny) to prove engine portability | Medium | 4 h | Tier 1 | Medium — nice closing beat |
| 3.4 | Voice-triggered goals | Low | 2 h | 1.4 | Low — cut first |

## Sequencing notes

- Build 1.1 before anything AI. A polished Meridian makes every later feature look real.
- 2.2 (Runloop) has the most integration risk — spike it early with a hello-world devbox even during Tier 1, so surprises surface with time to react.
- Rehearse the sabotage (demo step for 2.5) with a scripted, reversible UI change — one env var that renames/moves a control — never a live code edit on stage.
- If time collapses: cut 2.4/2.5 *last* — a scripted-but-real single-plan heal is worth more than three polished stretch features.
