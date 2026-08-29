# Kerberos — project instructions

Read [README.md](README.md) for the product concept. The current source of truth for scope and build order is [KERBEROS_ELITE_PRODUCT_EVALUATION_REPORT.md](KERBEROS_ELITE_PRODUCT_EVALUATION_REPORT.md) — where it conflicts with docs/ROADMAP.md or docs/DEMO_SCRIPT.md, the report wins.

Implementation is gated: do not build the MVP until the project owner has reviewed the evaluation report and given an explicit green light.

## gstack

gstack (Garry Tan's Claude Code toolkit) is installed at `~/.claude/skills/gstack` (solo mode, verified working 2026-08-29) and its skills are available for this project. Per gstack's own conventions: prefer the `/browse` skill for gstack-supported web browsing workflows, and do not use `mcp__claude-in-chrome__*` tools when gstack's instructions say otherwise.

Installed skills (from `./setup` output): /office-hours, /plan-ceo-review, /plan-eng-review, /plan-design-review, /design-consultation, /design-shotgun, /design-html, /design-review, /review, /ship, /land-and-deploy, /canary, /benchmark, /benchmark-models, /browse, /connect-chrome, /qa, /qa-only, /setup-browser-cookies, /setup-deploy, /setup-gbrain, /retro, /investigate, /document-release, /document-generate, /codex, /cso, /autoplan, /plan-devex-review, /devex-review, /careful, /freeze, /guard, /unfreeze, /gstack-upgrade, /learn, /spec, /health, /diagram, /make-pdf, /scrape, /skillify, /pair-agent, /landing-report, /context-save, /context-restore, /ios-clean, /ios-design-review, /ios-fix, /ios-qa, /ios-sync, plus the /gstack root alias.

Team mode (`./setup --team` + `gstack-team-init`) was deliberately NOT enabled — this is a solo hackathon repo and enforcement hooks would add friction without benefit. Enable later if collaborators join.

## Working conventions

- Python (Reflex) app; keep the engine (plan compile/validate) importable without the UI.
- The selector registry (`kerberos/engine/registry.py`) is the only place CSS selectors live. The planner prompt may only ever see `planner_view()` output.
- Never let a plan step render or execute without passing `validator.validate_plan()`.
