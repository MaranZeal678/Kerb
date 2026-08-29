# Kerberos MVP Specification — v1.0 (Green-Light Document)

**Status: FINAL, awaiting owner green light. This document responds to every finding in [KERBEROS_ELITE_PRODUCT_EVALUATION_REPORT.md](KERBEROS_ELITE_PRODUCT_EVALUATION_REPORT.md), folds the accepted changes into a complete working model of the system, and supersedes all prior docs on conflict.**

---

# PART 1 — RESPONSE TO THE GSTACK EVALUATION

Every finding, answered on the record. **A** = accepted as-is, **A±** = accepted with a modification (reason given), **R** = rejected (reason given).

| # | Finding (review) | Response | Design consequence (where in this spec) |
|---|---|---|---|
| 1 | Runloop clone bootability is the single point of collapse; spike first (Eng 🔴R1) | **A** | Build gate G0: 2h spike with a written pass/fail rubric and a pre-decided fallback (§7.4, §10 Phase A) |
| 2 | Judge-driven sabotage, not scripted (Office-hours + Red team) | **A** | Sabotage panel is a first-class component with its own contract (§6.6); scripted mode kept ONLY as a rehearsal harness, never on stage |
| 3 | Spine-first build order; heal loop ugly-but-real by midpoint (CEO/Office-hours 🔴R3) | **A** | Build gate G1 at end of Phase C: full break→detect→repair→verify loop on video before any Phase D/E work (§10) |
| 4 | Replace "model confidence" with computable grounding (Eng 🟠) | **A** | Grounding formula + thresholds specified exactly (§4.3); the phrase "model confidence" is banned from UI and narration |
| 5 | Page-state mismatch: plans need route preconditions (Eng 🔴) | **A** | `route` field on every step; validator rule V4; executor navigate-or-halt behavior (§4.1, §4.4, §5.2) |
| 6 | Live-execution race with user input (Eng 🔴) | **A** | Input freeze is part of the Autopilot renderer contract, with a visible "hands-off" scrim (§5.3, §8) |
| 7 | Heal-to-wrong-target is worse than staying red (Eng 🟠) | **A** | Repair agent constrained to evidence-based matching; patch must carry evidence chips, pass validator, and green re-replay before merge; registry is versioned with one-click rollback (§6.4, §4.2) |
| 8 | On-stage latency: <60s heal, no dead air (Eng 🟠 + Demo killer) | **A±** | Accepted the budget; **modified the mechanism**: not a devbox *pool* (over-engineered for one demo) but a two-box strategy — one warm standby + one active, refreshed after each use. Simpler, same latency, lower cost (§7.3) |
| 9 | Copilot demoted from headline act to visible gate (CEO 🟡) | **A** | Copilot is a dial position with a 15-second demo beat; its renderer is the Guide renderer + execute-on-confirm (§5.3) |
| 10 | No chat window; ⌘K command bar only (Design) | **A** | Command bar contract in §8; there is no free-form chat surface anywhere in the product |
| 11 | ModeRenderer isolation to prevent conditional spaghetti (Eng) | **A** | One shared state, three renderer classes, two executor adapters behind one interface (§5.1, §5.2) |
| 12 | Mock-app discount is near-fatal; defuse it (Red team 🔴) | **A±** | Instrumentation-diff slide + judge sabotage accepted. **Modified**: second demo app stays a stretch (Phase E5) — but the registry/engine are spec'd app-agnostic from day one (nothing imports Meridian), so the portability claim is architecturally true even if E5 is cut (§4.2, §6.1) |
| 13 | Kerberos name collides with the auth protocol (CEO ⚠️) | **R** (keep the name) | The collision is survivable and the mythology is doing real narrative work ("three heads, one body" structures the whole pitch). Mitigation stands: watchdog framing lands in the first 10 seconds. Rename remains a 10-minute decision if a sponsor objects |
| 14 | PostHog AI collision (owner-requested check) | **A** | Vocabulary guardrails are binding spec, not advice: "re-runs"/"verification board," never "session replay"/"analytics"/"insights"/"dashboard"; pitch leads with the artifact (§9.4) |
| 15 | Animated dial skeuomorphism (Design, low impact/med cost) | **R** (cut) | Segmented control with theme morph delivers the transformation feel at a fraction of the cost (§8.2) |
| 16 | Escalation card as demo insurance (Demo killer) | **A** | Promoted to P1 with its own acceptance criterion — it is the rehearsed answer to an unhealable judge sabotage (§6.5, §9.3) |
| 17 | Frustration signals / extra confidence inputs (Eng, evaluated) | **R** | Low impact per hour at hackathon scope; grounding + escalation cover the honesty story |
| 18 | Voice input, analytics dashboard (Pruning 🔴) | **A** (stay cut) | Not in this spec; a single success-rate stat lives on the verification board tile (§6.3) |

Net: 14 accepted (2 with modifications), 3 rejected with reasons, 1 kept-cut. The four binding conditions from the report's §13 are implemented as **hard build gates** G0–G3 (§10), so accepting this spec automatically satisfies them.

---

# PART 2 — THE COMPLETE WORKING MODEL

## §1. System overview

One artifact — the **Guide Plan** — flows through one pipeline and is consumed by four projections:

```
                    ┌────────────────────────────────────────────┐
 policy docs ──►  RAG ──► PLAN COMPILER ──► VALIDATOR ──► PLAN STORE
                    ▲            ▲                            │
              registry.planner_view()                        │ (same plan object)
                    │                                        ▼
             SELECTOR REGISTRY ◄── repair patches   ┌──── PROJECTIONS ────┐
                    ▲                               │ Guide    (render)   │
                    │                               │ Copilot  (confirm)  │
             REPAIR AGENT ◄── red replays ◄─────────│ Autopilot(execute)  │
                    │                               │ Sentinel (re-run)   │
                    └── green re-replay gate        └─────────────────────┘
                         (Runloop devboxes)
```

Repo layout (already scaffolded):

```
kerberos/            Reflex app: shell, dial, renderers, overlay, command bar
  engine/            registry.py · planner.py · validator.py · rag.py · executor.py
  meridian/          demo app (imports NOTHING from engine; engine imports NOTHING from meridian)
sentinel/            replay.py (devbox runner) · heal.py (repair agent)
plans/               plan store (JSON files)
docs/policy/         the 4 seeded policy docs
```

## §2. Meridian — the demo stage (full spec)

A mock insurance claims back-office. Three screens, 12 registered controls, seeded data engineered to make every demo beat fire deterministically.

**Screens & controls (registry ids):**

| Screen | Route | Controls |
|---|---|---|
| Claims list | `/claims` | `claims.search` (fill) · `claims.filter.status` (select) · `claims.row.open` (click) |
| Claim detail | `/claims/{id}` | `claims.refund.start` (click) · `claims.notes.add` (fill) · `claims.status.set` (select) · `claims.docs.open` (click) |
| Refund modal | `/claims/{id}` (modal) | `claims.refund.amount` (fill) · `claims.refund.reason_code` (select) · `claims.refund.memo` (fill) · `claims.refund.approve` (click) · `claims.refund.cancel` (click) |

**Seeded data (deterministic demo):**
- Claim **#4821** — $612.50 (crosses the $500 policy threshold → plan gains `reason_code` + `memo` steps → the "it read the policy" beat)
- Claim **#3377** — $180.00 (below threshold → visibly shorter plan; the A/B that proves policy-dependence)
- Claim **#5150** — status `disputed` (refunds on disputed claims are policy-forbidden → escalation card beat)
- 9 filler claims for realistic list density.

**Policy docs (RAG corpus, ~2–3 pages each):** `refund-policy.md` (the $500 rule, §4.2 reason codes), `reason-codes.md` (RC-01…RC-12 semantics), `escalation-matrix.md` (disputed claims, supervisor rules), `sla.md` (distractor doc — proves retrieval selectivity).

**Sabotage hook:** Meridian renders every control's label/placement from a runtime `overrides` dict keyed by registry id (§6.6). No code edits on stage, one-keystroke reset.

## §3. The Guide Plan — canonical schema (v1)

```json
{
  "plan_id": "pln_4821_refund_r3",
  "goal": "Issue a refund for claim #4821",
  "docs_version": "d7", "registry_version": 3,
  "status": "validated",
  "sources": [
    {"doc": "refund-policy.md", "chunk": 14, "score": 0.91},
    {"doc": "reason-codes.md",  "chunk": 3,  "score": 0.84}
  ],
  "steps": [
    {
      "id": 4,
      "route": "/claims/4821",
      "selector": "claims.refund.reason_code",
      "action": "select", "value": "RC-07",
      "why": "Refunds over $500 require a reason code",
      "citation": {"doc": "refund-policy.md", "chunk": 14},
      "grounding": 0.86,
      "autonomy_ceiling": "autopilot"
    }
  ]
}
```

Field semantics: `route` = precondition the executor must satisfy before acting (navigate-or-halt); `grounding` and `autonomy_ceiling` computed at compile time (§4.3); `value` may be a literal or a `{"from": "goal.entity.amount"}` binding resolved at compile time — the executor never invents values. Plans are immutable; a re-compile creates a new `plan_id` revision. Every mode consumes this object verbatim — the on-screen plan id in all four modes is the proof-of-one-engine detail.

## §4. The engine

### §4.1 Plan compiler (`engine/planner.py`)
Input: goal + top-k retrieved chunks (with scores) + `registry.planner_view()` (logical ids, labels, allowed actions, routes — **never CSS**). One Mistral chat call, JSON-constrained to the schema above minus computed fields. Deterministic post-pass computes grounding, ceilings, and validates. Cache key: `(goal_normalized, docs_version, registry_version)` — demo goals pre-warmed; a registry patch invalidates affected plans (Sentinel recompiles them, which is itself part of the self-healing story).

### §4.2 Selector registry (`engine/registry.py`)
`Control{id, selector, label, aria_hints, actions, route, version}`. The **only** file in the system containing CSS. App-agnostic: Meridian's instrumentation constants *generate* registry entries, not the reverse — a second app is a second constants file (the architectural answer to the mock-app discount). Versioned: repair patches append `RegistryPatch{patch_id, control_id, old, new, evidence[], replay_proof, ts}`; any patch is one-click rollback.

### §4.3 Grounding & autonomy ceilings (computed, never vibes)
```
citation_coverage(step) = fraction of the step's why/value tokens entailed by its cited chunk (lexical overlap vs the chunk, 0..1)
grounding(step)         = retrieval_score(citation) × citation_coverage(step)

ceiling: grounding ≥ 0.75 → autopilot   |   0.45–0.75 → copilot (forced confirm)   |   < 0.45 → guide-only
plan-level: any step < 0.45 that is REQUIRED → escalation card instead of a plan
effective autonomy per step = min(dial_position, step.autonomy_ceiling)
```
Demo lever: `claims.refund.memo`'s policy text is deliberately vague in the corpus → its grounding lands in the copilot band → the forced-confirm beat fires deterministically.

### §4.4 Validator (`engine/validator.py`) — pure Python, no LLM, nothing renders or executes without it
V1 selector exists in registry · V2 action allowed for that control · V3 value type matches control (select values ∈ enum; fills match declared type) · V4 route reachable: step N's route must equal step N−1's route or be reachable via a declared transition (e.g. `claims.row.open: /claims → /claims/{id}`) · V5 ceiling present and consistent with grounding bands · V6 plan ≤ 12 steps (latency budget) · V7 repair patches only: evidence non-empty and `replay_proof` green. Failures are named, user-visible cards ("rejected by V4: step 3 acts on /claims/4821 but the plan never navigates there") — zero silent failures.

## §5. Modes — one state, three renderers, two executors

### §5.1 Reflex state (single source of truth)
```python
class KerberosState(rx.State):
    mode: str            # "guide" | "copilot" | "autopilot"
    plan: dict           # the validated Guide Plan (verbatim)
    step_idx: int
    executing: bool      # True freezes Meridian input (scrim on)
    receipt: dict        # sandbox rehearsal receipt (autopilot)
    board: list[dict]    # sentinel tiles [{plan_id, status, patch?}]
    sabotage: dict       # active overrides {control_id: {label?, slot?}}
```
Mode switch = one event → theme tokens + renderer swap, <400ms. Nothing about the plan changes — visibly the same `plan_id`.

### §5.2 Executor interface (the anti-spaghetti boundary)
```python
class Executor(Protocol):
    def run(self, plan, from_step=0, confirm_cb=None) -> Iterator[StepResult]
    # StepResult{step_id, status: ok|failed|awaiting_confirm|halted, screenshot?, dom_snapshot?, note}
```
- **LiveExecutor** (in-app): satisfies `route` by driving Reflex navigation state; performs actions by mutating the same state the human would; emits ticker lines; on failure → halt + named card + Sentinel ticket. Runs only while `executing=True` (input frozen).
- **SandboxExecutor** (devbox): Playwright against the Meridian clone; same interface; captures per-step screenshots + DOM snapshot on failure. Used by both the Autopilot rehearsal and Sentinel — **one replay machinery, two callers.**

### §5.3 Renderers
- **GuideRenderer**: spotlight cutout on current control, beacon, step card (`why` + citation chip), docs panel; advances by *observing* the user's own action on the highlighted control. Teal theme.
- **CopilotRenderer**: GuideRenderer + "Do it" per step via LiveExecutor with `confirm_cb`; steps in the copilot band render an amber forced-confirm card ("weakly grounded — confirm or skip"). Amber theme.
- **AutopilotRenderer**: (1) SandboxExecutor rehearsal → receipt (filmstrip + state diff) → explicit Run; (2) LiveExecutor full run, page dimmed, input frozen, reasoning ticker. Violet theme. Any step whose ceiling < autopilot pauses for confirm — the dial can never override a ceiling.

## §6. Sentinel & the heal loop (the wow, fully specified)

### §6.1 Replay
`sentinel/replay.py`: for each stored plan → warm devbox → SandboxExecutor.run → tile `green` or `red{failed_step, dom_snapshot, screenshots}`. On stage it runs on demand; the "nightly" framing is narration of the same loop on a schedule.

### §6.2 States
`green → red → healing → green(patched)` or `→ escalated`. Tiles animate through these on the verification board.

### §6.3 Verification board
Plan tiles: goal, status lamp, last-verified time, one success-rate stat. A red tile expands to failed step + snapshot; a healing tile shows the patch diff. **Never called a dashboard.**

### §6.4 Repair agent (`sentinel/heal.py`)
Input: failed step + old registry entry + fresh DOM snapshot. Prompt constraints: may only propose a patch for the failed control; must cite evidence from the snapshot (label text match, aria role, relative position); must return `{control_id, new_selector, new_label, evidence[], rationale}`. Merge gate = V1–V5 + V7 + **green re-replay in a fresh devbox**. UI renders the patch as a two-line PR with evidence chips. No candidate with sufficient evidence → `escalated`, with the agent's reasoning shown — honesty as a feature.

### §6.5 Escalation card
Fires on: required step below grounding floor, policy-forbidden goal (claim #5150), or unhealable sabotage. Contents: what was attempted, the partial plan, the exact blocker (named rule or missing evidence), and a handoff summary. This is both a product feature and the rehearsed safe landing for any judge input we can't handle.

### §6.6 Sabotage panel (judge-facing)
Dropdown of registered controls → new label text and/or new slot (each screen declares 2–3 alternate layout slots per control — a *bounded* but real move space). Writes to `state.sabotage`; Meridian re-renders instantly; one-keystroke reset. Bounded honestly: renames are free-text, moves are slot-based — and the presenter says so if asked ("labels are free-text; positions move between real layout slots").

## §7. Runloop integration

- **§7.1 Snapshot blueprint** (built once in Phase A): Python + Meridian in headless mode (`MERIDIAN_HEADLESS=1`: engine + app server, no compile calls — plans arrive as JSON) + Playwright + chromium + seeded DB. No Mistral key inside devboxes; sandboxes execute, they never think.
- **§7.2 Lifecycle:** create-from-snapshot → inject `{plan.json, sabotage.json}` → run replay script → collect `{result.json, screenshots/, dom_snapshot.html}` → destroy.
- **§7.3 Warm-standby strategy** (modified from the eval's "pool"): keep exactly one warm standby devbox; on use, promote it and asynchronously create the next. Latency budget: rehearsal ≤ 20s; full heal loop (red → patch → green re-replay) ≤ 60s, rehearsed.
- **§7.4 Gate G0 spike rubric (pass = all four):** boot from snapshot ≤ 30s · replay the 8-step refund plan green · sabotaged replay produces red + DOM snapshot · artifacts retrievable. **Fail ⇒ pre-decided fallback:** local headless-Chromium subprocess behind the same `SandboxExecutor` interface (one file swap), disclosed honestly in the tech reveal.

## §8. UX specification

- **§8.1 Layout:** Meridian is the full canvas. Kerberos = slim top bar (wordmark · dial · plan id · mode badge) + ⌘K command bar + right rail that exists only when a plan is active. A layer over software, not a website. No chat surface exists.
- **§8.2 Dial:** segmented 3-position control. Switch = theme token cross-fade + rail morph, 300ms, one easing curve. Guide teal `#0E7C6B` / Copilot amber `#C4820E` / Autopilot violet `#6C5CE0` on a dark `#17151E` ground; mode badge always visible.
- **§8.3 Command bar:** ⌘K, goal autocomplete from seeded goals, free text allowed. Compile renders as streaming retrieval chunks (doc + score chips) resolving into steps. No spinners anywhere in the product.
- **§8.4 Spotlight:** full-canvas dim with cutout, soft beacon, step card anchored with arrow: one bold action line, one `why` line, citation chip.
- **§8.5 Receipt:** horizontal filmstrip of per-step screenshots + single before/after state diff ("Claim #4821: status open → refunded · $612.50 issued · RC-07") + Run / Cancel.
- **§8.6 Ticker:** one line per step, mono, e.g. `▸ step 4/8 — reason code RC-07 (policy §4.2) · grounded 0.86`.
- **§8.7 Motion discipline:** 200–400ms, state-change only, `prefers-reduced-motion` honored.

## §9. Demo runbook (4:00) — beats unchanged from report §10, with these bindings
- **§9.1** Cold open Autopilot (0:05–0:20) runs on the **pre-warmed cached plan**; live compilation happens only in Guide.
- **§9.2** The policy beat uses the #4821 vs #3377 plan-length contrast if a judge asks "how do I know it read the docs?"
- **§9.3** Judge sabotage: rename/move → red → patch-with-evidence → green re-replay → live spotlight on the judge's renamed control (≤ 60s, rehearsed ≥ 10×). Judge deletes/asks the impossible → escalation card beat, also rehearsed.
- **§9.4** Vocabulary guardrails (binding): "Sentinel **re-runs** every guide in a sandbox" · "**verification board**" · never "session replay," "analytics," "insights," "dashboard," or "model confidence" · pitch leads with the artifact, never "AI that navigates a UI."
- **§9.5** Fallbacks staged before the demo: recorded receipt + heal clips (labeled as recordings if used), sabotage reset key, local-sandbox flag.

## §10. Build plan with hard gates (2 builders, ~35h P0/P1)

| Gate | Condition (from report §13) | Pass criterion |
|---|---|---|
| **G0** (before all else) | Runloop spike first | §7.4 rubric passes, or fallback consciously invoked and logged |
| **G1** (end Phase C, hackathon midpoint) | Spine first | Unedited video: judge-style rename → red → patch → green → live re-run |
| **G2** (end Phase D) | Honest confidence | Forced-confirm beat fires from real grounding numbers; banned vocabulary absent from UI |
| **G3** (before demo) | Judge-driven sabotage | 10 consecutive clean rehearsals incl. 2 escalation-path runs; heal ≤ 60s |

Phases (tasks/estimates as report §12): **A** Foundation & spike ~5h → **B** Core (RAG, compiler, validator, Guide) ~9h → **C** Wow spine (sandbox executor, sabotage panel, repair agent, minimal board) ~8h → **D** Full dial (live executor, receipt, copilot gate, escalation card) ~6h → **E** Hardening (theming, caches, rehearsals, instrumentation slide; E5 second app only if all else done) ~7h.

**Per-feature acceptance criteria (definition of demo-ready):** Compiler: 5 seeded goals compile valid in ≤ 8s warm-cache / ≤ 20s cold · Guide: full #4821 walkthrough with citations, zero unhighlighted steps · Copilot: memo step forces confirm every run · Autopilot: rehearsal receipt ≤ 20s; live run completes with input frozen · Sentinel: board reflects true replay state; no fake green · Heal: label rename and slot move both heal ≤ 60s; control deletion escalates with reasoning · Escalation: #5150 refund produces the card, never a plan.

---

# §11. GREEN-LIGHT CHECKLIST

Approving this spec means approving, specifically:

1. **The four conditions are now build gates G0–G3** — they cannot be skipped without a logged decision.
2. **Two modified acceptances:** warm-standby devbox pair instead of a pool (§7.3); second app remains stretch, with app-agnosticism guaranteed architecturally instead (§4.2).
3. **Two rejections:** the name **Kerberos** stays (framing mitigation, rename reserved as a 10-minute fallback); dial skeuomorphism stays cut.
4. **Scope is frozen** to §4 features + §6 wow + §6.5/§8 support surface. Anything else is a new decision, not scope drift.

**Reply "GREEN LIGHT" to start Phase A (the Runloop spike G0 is the first action). Reply with any § number to renegotiate that item first.**
