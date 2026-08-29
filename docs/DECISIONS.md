# Decision Log

## D-001 · 2026-08-29 · Gate G0: Runloop fallback invoked
**Decision:** SandboxExecutor runs on the pre-decided local fallback — headless Chromium via Playwright driving an isolated browser session against the app — instead of Runloop devboxes.
**Reason:** No `RUNLOOP_API_KEY` is present in this environment, so the §7.4 spike cannot pass its rubric (devbox creation requires credentials). Spec §7.4 pre-decided exactly this fallback: same `SandboxExecutor` interface, one adapter swap when a key arrives.
**Consequence:** The `RunloopSandbox` adapter is stubbed key-ready in `kerberos/engine/executor.py`; the demo tech-reveal narration must disclose "local sandbox" honestly until a key is added. All Sentinel/heal behavior is identical either way.

## D-002 · 2026-08-29 · Plan compiler: Mistral-first with deterministic fallback
**Decision:** `compile_plan` tries Mistral (JSON-constrained) first and falls back to a deterministic compiler on any error/timeout; every plan is tagged `compiler: "mistral" | "deterministic"`.
**Reason:** Demo determinism is a G3 requirement; API latency/outage cannot be allowed to kill a beat. The deterministic path uses the same RAG retrieval, grounding math, and validator — only step *authoring* differs.

## D-003 · 2026-08-29 · Receipt renders step rows, not screenshot filmstrip
**Decision:** The Autopilot receipt UI shows per-step verified rows + before/after state diff; sandbox screenshots are still captured to disk (`plans/receipts/`) but not rendered in-app for MVP.
**Reason:** Runtime-generated assets aren't reliably served by the dev asset pipeline; rows + diff carry the demo beat. Filmstrip is a Phase E polish item.

## D-004 · 2026-08-29 · Sandbox replay runs as a subprocess; receipts live outside the project
**Decision:** `SandboxExecutor` spawns `scripts/replay_cli.py` as its own OS process (with `PYTHONDONTWRITEBYTECODE=1`), and receipt screenshots write to `~/.kerberos/receipts`, never into the repo.
**Reason:** Two debugging discoveries: (1) Playwright-in-thread inside the backend intermittently wedged; a subprocess is fully isolated and closer to the devbox model anyway. (2) The Reflex dev file-watcher hot-reloads the backend on `.png` writes (and stale `__pycache__` regeneration) inside the project tree, which drops every websocket mid-replay — the sandbox session's click events were being lost to our own screenshots.

## D-005 · 2026-08-29 · Registry patches persist to disk
**Decision:** Repair patches live in `~/.kerberos/registry_patches.json`, loaded on every `registry()` call.
**Reason:** The green re-replay runs in a separate process; in-memory patches never reached it. File-backed patches give every process the same registry version, plus a durable, rollback-able trail — which spec §4.2 wanted anyway.
