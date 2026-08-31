# Kerb - System Architecture

This document explains how Kerb is built and, more importantly, why it is built this way. The reference contracts live in [SPEC.md](SPEC.md); decisions taken under constraint live in [DECISIONS.md](DECISIONS.md).

## The organizing idea

Kerb has exactly one first-class object: the **Guide Plan**. Everything upstream exists to author and admit one; everything downstream is a projection of one.

This is the whole architecture in a sentence, and it produces the system's unusual properties almost for free. Because a plan is data rather than prose, it can be executed. Because it can be executed, it can be replayed. Because it can be replayed, it can be verified. Because it can be verified, it can be repaired. A system whose guidance is written as English paragraphs has none of these affordances, which is why documentation everywhere rots quietly and automation everywhere breaks loudly.

```
                         one artifact, four readings

   author  ─────────────►  Guide Plan  ─────────────►  render     (teach)
                              │  ▲                     execute    (assist)
                              │  │                     rehearse   (perform)
                              ▼  │                     replay     (verify)
                          repair ─┘
```

## Authoring path

A stated outcome becomes an admitted plan through four stages, in this order. The order is a safety property, not an implementation detail.

### 1. Policy gate — `engine/planner.py: policy_gate`

Eligibility is decided *before* any plan is authored. Is this a goal the system is permitted to plan at all? A refund against a disputed claim is prohibited by policy, so it never reaches a compiler; it returns a handoff naming the blocking rule.

This placement is the point. If eligibility were checked inside a compiler, a sufficiently fluent model-authored plan could route around a prohibition simply by not mentioning it. Because the gate runs first and is compiler-independent, no authoring strategy can produce a plan for a forbidden outcome.

### 2. Retrieval — `engine/rag.py`

Policy documents are chunked on heading boundaries, embedded, and retrieved by cosine similarity. Each retrieved chunk carries its score forward into the plan, because those scores are later used as evidence and must survive to the artifact.

With no endpoint configured, retrieval falls back to IDF-weighted lexical scoring over the same chunks. The fallback is not a degraded mode bolted on for demos; it is what keeps the system's guarantees independent of a network.

### 3. Compilation — `engine/planner.py`

The compiler receives the goal, the retrieved policy, and `registry.planner_view()` — logical control ids, human labels, permitted actions, and routes. **It never receives a selector.** This is the difference between constraining a model with instructions and constraining it structurally: a control that is not registered cannot be named, so it cannot be acted upon, so hallucination becomes a compile-time rejection rather than a runtime hazard.

Two strategies author plans behind one interface. The model strategy writes fluent, policy-quoting steps. The deterministic strategy encodes the flow directly. Model output that fails grading is not treated as an escalation — the deterministic compiler simply authors the plan instead. The user's experience of a slow, absent, or poor endpoint is a plan phrased more plainly, never a missing plan.

### 4. Grading and validation — `engine/planner.py: _postpass`, `engine/validator.py`

Grading is applied *after* authoring by code neither compiler controls:

```
grounding(step) = retrieval_score(cited chunk) x citation_coverage(step)

    >= 0.75   may run unattended
0.45 - 0.75   must be confirmed, whatever the dial says
     < 0.45   escalate rather than perform
```

`citation_coverage` is the fraction of a step's justification that is actually supported by the chunk it cites — computable, inspectable, and impossible for the model to inflate by asserting confidence. This is deliberate: a model's self-reported certainty is not evidence, and treating it as evidence is the most common way these systems mislead people.

The validator then runs as plain Python with no model in the path. It checks registration, permitted action, value type, **route reachability** (step N's route must follow from step N-1, so a plan cannot act on a page the flow never reaches), and that no step claims more autonomy than its grounding supports. Failures are named and surfaced, never swallowed. Nothing renders or executes without passing.

## Projection path

One state object holds the mode, the plan, and the cursor. Switching modes re-projects; it never recompiles, and the visible `plan_id` does not change — which is how "one engine, three behaviors" is demonstrated rather than claimed.

| Mode | Projection |
|---|---|
| Guide | Spotlight on the current control, justification and citation beside it; advances when the operator acts on the highlighted control |
| Copilot | Proposes and performs each step on confirmation; a step in the confirm band stops regardless of the dial |
| Autopilot | Rehearses in an isolated sandbox, presents a receipt, then performs live with the surface frozen |

Effective autonomy for a step is `min(selected_mode, step.autonomy_ceiling)`. The dial raises a ceiling for the session; it cannot raise the ceiling on a step whose evidence does not support it.

### Two executors, one interface

Live execution mutates the same application state a human interaction would, so there is no separate "automation surface" that can drift from the real one. Sandbox execution drives a real browser session against a fresh instance. Both satisfy one interface, which is why rehearsal, scheduled verification, and repair validation all exercise the identical code path an operator does.

## Verification and repair

```
   stored plans
        │
        ▼
   replay in isolated sandbox ──── clean ────► board: passing
        │
      failure + page evidence
        │
        ▼
   repair agent: match on role, region, visible label
        │
        ├── evidence supports one candidate ──► patch ──► validate ──► re-run
        │                                                                │
        │                                                    clean ──────┴──► admit as new registry version
        │
        └── evidence insufficient ──► escalate with reasoning
```

The repair agent is constrained the same way the compiler is. It may only propose a replacement for the control that actually failed, chosen from controls observed on the changed page that are unregistered and role-compatible with the failed action. Where several candidates survive that filter, a model breaks the tie — but it selects *among evidence*, and cannot introduce a candidate the page did not contain.

A patch is admitted only after it passes validation and re-executes cleanly. This ordering matters more than it appears: a repair that turns a failing plan green by pointing at the wrong control is worse than the failure it replaced, because it converts a visible problem into an invisible one.

The registry is versioned and patches append rather than overwrite, so any admitted repair carries its evidence and its proof and can be rolled back.

## Design commitments

**The model is the weakest component by construction.** It proposes wording and breaks ties. It does not decide eligibility, does not choose what it is allowed to touch, does not grade itself, and does not reach the live interface before a sandbox does. Disable it entirely and the system still produces correct, conservative plans.

**Failures are named.** A rejected plan reports the rule that rejected it. An escalation reports the blocking policy and what had already been done. A repair that cannot be justified reports why. Silent degradation is the failure mode that makes systems like this untrustworthy, so there is none.

**Selectors live in exactly one place.** The registry is the sole location where a logical control id maps to something concrete. Adapting Kerb to another application is an exercise in describing controls, not in modifying the engine — nothing in `kerb/engine` imports the bundled demonstration application.

**Boring where it is allowed to be.** In-memory vectors, JSON files for plans, a subprocess for isolation. Complexity is spent on the verification loop, which is the part that is actually hard.
