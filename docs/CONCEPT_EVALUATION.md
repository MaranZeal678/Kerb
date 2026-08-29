# Concept Evaluation — how Kerberos won

Record of the Phase 1–3 exploration: what's overdone, the 10 candidates, and the brutal scoring that selected Kerberos.

## Phase 1 — What judges have already seen too many times (2026)

**Instantly forgettable:** chat-with-your-PDF and every RAG chatbot variant; "AI copilot for X" that is a system prompt plus an API wrapper; multi-agent org charts (Researcher→Critic→Writer) that produce a markdown file; dashboards with an LLM summary pane; voice skins; demos where the AI only *talks about* the app instead of touching it.

**What reads as genuinely different in 2026:**
1. **The AI acts on a real interface, visibly** — cursor moves, forms fill, and the audience can see it.
2. **Legible safety** — autonomy with inspectable guardrails, not "trust us."
3. **Self-maintaining systems** — anything that closes its own loop (test → fail → repair) reads as a platform, not a demo.
4. **One sharp mechanism** demonstrated four ways beats four shallow features.
5. **Honest confidence** — a system that visibly knows what it doesn't know.

**Strategic verdict on the original framing:** a multi-use-case toggle across *verticals* (support mode / education mode / healthcare mode) is a trap — it reads as five shallow apps behind tabs, exactly what the brief fears. The toggle only becomes powerful if it dials a **dimension of the same task**. The strongest dimension available, given DOM-guidance + RAG foundations, is **autonomy/trust**. That reframe drove the shortlist.

## Phase 2 — The 10 candidates

Each entry: pitch · toggle · DOM/RAG role · why it can't be a chatbot · feasibility.

1. **Sherpa** — universal in-app onboarding overlay; toggle = viewer persona (new hire / power user / auditor) re-lensing the same screen. DOM highlights per persona; RAG on role docs. Not-a-chatbot: it points, doesn't describe. Feasible, but toggle = content filter — weak transformation. 
2. **Kerberos** — one guidance engine, toggle = autonomy dial (Guide/Copilot/Autopilot) + Sentinel self-testing in sandboxes. DOM is the execution substrate; RAG grounds every plan; plans double as regression tests. Not-a-chatbot: the artifact is an executable, validated plan. Feasible core; Runloop loop is the stretch.
3. **Dojo** — SOP training simulator; toggle = teach mode vs exam mode (AI watches you drive and grades against policy). DOM observation both ways; RAG = rubric. Memorable inversion (AI grades human) but exam mode is hard to make reliable in a weekend.
4. **Prism** — accessibility transformer; toggle = motor/low-vision/cognitive profiles changing how guidance renders. High social value; technically it's mostly CSS + pacing — thin AI story, and doing it *badly* in a demo is worse than not doing it.
5. **Ledger** — compliance walkthrough auditor; toggle = regulation regime; AI walks flows collecting evidence vs policy (RAG). Real enterprise value, visually dry, "audit report" is a PDF — judges nap.
6. **Cartographer** — agent explores any unknown app in a sandbox and auto-generates tours/docs; toggle = audience. Spectacular if it works; autonomous exploration of arbitrary apps is a research project, not a weekend. Demo would be faked or fragile.
7. **LivingDocs** — documentation that drives the UI: reading a doc highlights/executes the real steps; toggle = product version/role. Strong "show don't tell"; overlaps Kerberos Guide mode but lacks the autonomy arc and self-healing.
8. **Two-Sides** — support cockpit; toggle flips between agent view and customer view of the same live session. Cute symmetry, but each side is roughly a chatbot with context — fails the core test.
9. **Playback** — every tutorial is also a Playwright test; toggle = guide mode vs test mode; CI for documentation. Technically lovely, visually a test runner. Best absorbed as a *capability* of #2, not a product.
10. **Kiosk** — public-services form helper; toggle = language/literacy level. High social value, very feasible, and completely forgettable next to autonomous execution — the toggle is localization.

## Phase 3 — Brutal scoring (1–10)

| # | Concept | Innov | Wow | Tech | Value | Memor | Toggle | Feas | **Overall** |
|---|---|---|---|---|---|---|---|---|---|
| 1 | Sherpa | 6 | 6 | 6 | 8 | 5 | 6 | 8 | 6.0 |
| 2 | **Kerberos** | 9 | 9 | 9 | 8 | 9 | 10 | 7 | **8.8** |
| 3 | Dojo | 7 | 7 | 6 | 8 | 7 | 7 | 6 | 6.8 |
| 4 | Prism | 7 | 6 | 5 | 9 | 6 | 7 | 5 | 6.0 |
| 5 | Ledger | 6 | 4 | 7 | 8 | 5 | 6 | 5 | 5.5 |
| 6 | Cartographer | 9 | 9 | 9 | 7 | 9 | 5 | **3** | 6.0 |
| 7 | LivingDocs | 7 | 8 | 6 | 7 | 7 | 6 | 8 | 7.0 |
| 8 | Two-Sides | 5 | 6 | 5 | 7 | 5 | 6 | 7 | 5.5 |
| 9 | Playback | 8 | 6 | 8 | 8 | 7 | 6 | 7 | 7.2 |
| 10 | Kiosk | 5 | 6 | 4 | 8 | 5 | 7 | 8 | 5.5 |

**Winner: Kerberos (#2)**, deliberately absorbing Playback (#9 — plans-as-tests become Sentinel) and the best of LivingDocs (#7 — docs that drive become Guide mode). Cartographer scored equal on wow but its feasibility score of 3 is disqualifying — a hackathon demo that *might* work is a demo that doesn't.

**Why the toggle is finally meaningful:** Guide, Copilot, and Autopilot are provably the same engine — one state variable projecting one validated plan. The toggle demonstrates trust as a product dimension, which no vertical-tabs framing can.
