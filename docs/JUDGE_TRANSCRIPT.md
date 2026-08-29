# Kerberos — Judge-Facing Demo Transcript (~4:00)

Canonical spoken script. Vocabulary guardrails (spec §9.4) are baked in: never
"session replay" / "analytics" / "dashboard" / "model confidence"; Sentinel
"re-runs" guides; the board is the "verification board"; the artifact leads.
Stage directions in brackets. Rehearse until the sabotage beat is boring to you.

---

[Screen: Meridian full screen. Dial already on AUTOPILOT. No self-intro yet.]

"This is Meridian — a claims portal. The kind of software a million people
operate every day. Watch the screen, not me."

[⌘K → "Issue a refund for claim #4821." Receipt flashes; cursor moves; fields
fill; ticker narrates. ~12s. Done.]

"No macro. No script. It did that for the first time just now.

This is Kerberos — named for the three-headed watchdog. Three ways to trust one
guard dog. And a fourth head that never sleeps — which, in about two minutes,
YOU are going to test personally.

First, the problem. Every software company builds the same four things:
tutorials nobody reads, support docs that go stale, brittle automations, and UI
tests that snap every sprint. Four teams. Four vendors. But look closer —
they're all the same object: a sequence of steps against a real interface.
Kerberos builds that one artifact — we call it a Guide Plan — and this dial
changes only one thing: how much you trust it."

[Dial → GUIDE. Teal. Docs panel in. Point at the unchanged plan id.]

"Same request. Zero autonomy. Watch what happens BEFORE a single highlight
appears — it pulls the actual refund policy. Those are real retrieval scores.
Now it teaches me."

[Spotlight on first control.]

"It doesn't describe the button. It POINTS at it. Every step says why — and
cites the policy. And the detail I love: this refund is $612, so the plan grew
two extra steps — reason code, supervisor memo — because the policy requires
them above five hundred dollars. It read the RULES, not the pixels. Ask for
claim #3377 — a $180 refund — the plan gets shorter. Same brain. Different
policy path."

[Dial → COPILOT. Amber. Execute-on-confirm until the memo step halts.]

"One notch up: it does the work, I approve each step. And watch this one — it
stopped. The policy text behind this step is vague, its grounding score is low,
and Kerberos will not act on its own where it can't back the action with a
citation. It knows what it doesn't know — per step. You can turn the dial up.
You can't out-dial the evidence."

[Dial → AUTOPILOT. Violet. Page dims, input freezes. Open the receipt.]

"Full trust. But here's what the cold open hid from you: before it touched the
real screen, it had already performed the entire task in a disposable cloud
sandbox. This is the receipt — every step screenshotted, plus the
before-and-after. It rehearses. THEN it performs."

[Beat. Turn the laptop to the judge.]

"Now — the part every demo like this dreads. Software changes. So: break it.
Pick any control on this screen. Rename it. Move it."

[Judge renames Approve Refund, drags it to another slot. Re-run the guide — it
fails, visibly red.]

"You just did what every product team does every Tuesday — and somewhere, every
tutorial, bot, and test that depended on that button silently died. Ours too.
Now watch the fourth head."

[RUN SENTINEL. Verification board: red tile, failed step, DOM snapshot. Then a
two-line patch with evidence chips.]

"Sentinel re-runs every guide in a sandbox — there's the red. The repair agent
reads the wreckage and proposes exactly this — matched on YOUR label, YOUR
position. It refuses to merge until the fix re-runs green in a fresh sandbox…"

[Tile flips green. Re-run the guide live — spotlight lands on the judge's
renamed button.]

"…and live: it found YOUR button. Nobody filed a ticket. Nobody woke up. The
documentation fixed itself — and you're the witness, because you're the one who
broke it."

[One diagram: four layers.]

"Thirty seconds for the engineers. The model is trusted with nothing alone. It
can only reference a registry of approved controls — a hallucinated selector
isn't a risk, it's a compile error. Every plan passes a server-side validator —
pure code, no AI — before a single pixel moves. Grounding — retrieval score
times citation coverage — caps autonomy per step. And every execution rehearses
in a Runloop sandbox before it touches anything real. The interface is
pure-Python Reflex — this dial is literally one state variable, which is why I
can PROVE all four modes are one engine: same plan id, every mode. You watched
it."

[Close. Spin the dial slowly through teal, amber, violet.]

"Tutorials, support, automation, and QA were never four products. They're one
plan — at four levels of trust. Kerberos. Three heads, one body. And putting it
on your app is twelve data attributes.

Thank you."

---

## Contingency lines (rehearsed, spec §9)

- Judge deletes a control / asks the impossible → escalation card fires:
  "And when it CAN'T heal safely — it says so, shows its reasoning, and files
  the handoff. That honesty is the product."
- Runloop unreachable → labeled recordings for receipt/heal, all else live:
  "Sandbox link is down, so this clip is from rehearsal — everything else
  you're seeing is live."
- "Is this like PostHog AI?" → "PostHog AI tells you what happened in your
  product. Kerberos does the work inside any product — and proves its guidance
  still works every night."
