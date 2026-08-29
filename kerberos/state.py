"""Kerberos global state — the trust dial IS this state (spec §5.1).

One validated Guide Plan; mode is one variable; every mode is a projection.
The live executor lives here (it mutates the same state a human would).
"""

import asyncio
import copy
import json
import os

import reflex as rx

from .engine import planner, rag, store
from .engine import registry as regmod
from .engine.executor import replay as sandbox_replay
from .meridian import sabotage
from .meridian.data import SEED_CLAIMS

BASE_URL = os.environ.get("KERBEROS_BASE_URL", "http://localhost:3000")


def _plain(v):
    return json.loads(json.dumps(v))


class KState(rx.State):
    # ---- Meridian ----
    claims: list[dict] = []
    route: str = "claims"                 # claims | claim
    open_claim: dict = {}
    modal_open: bool = False
    search: str = ""
    filter_status: str = "all"
    refund_amount: str = ""
    refund_reason: str = ""
    refund_memo: str = ""
    note_text: str = ""
    toast: str = ""

    # ---- Kerberos ----
    mode: str = "guide"                   # guide | copilot | autopilot
    plan: dict = {}
    escalation: dict = {}
    rejected: list[str] = []
    step_idx: int = 0
    spotlight: str = ""
    compiling: bool = False
    chunks_view: list[dict] = []
    executing: bool = False
    awaiting: bool = False
    await_msg: str = ""
    ticker: list[str] = []
    receipt: dict = {}
    rehearsing: bool = False
    done_msg: str = ""
    cmd_open: bool = False

    # ---- Sentinel / sabotage ----
    sentinel_open: bool = False
    sentinel_busy: bool = False
    board: list[dict] = []
    sab_target: str = "claims.refund.approve"
    sab_label: str = ""
    sab_move: bool = False
    sab_nonce: int = 0

    # ================= computed =================
    @rx.var
    def ui(self) -> dict[str, str]:
        _ = self.sab_nonce  # dependency: recompute when sabotage changes
        out: dict[str, str] = {}
        for c in regmod.BASE:
            label, guide, moved = sabotage.eff(c.id, c.label)
            out[f"{c.id}.label"] = label
            out[f"{c.id}.g"] = guide
            out[f"{c.id}.moved"] = "1" if moved else "0"
        return out

    @rx.var
    def claims_view(self) -> list[dict[str, str]]:
        rows = self.claims
        if self.search.strip():
            q = self.search.strip().lower()
            rows = [c for c in rows if q in str(c["id"]) or q in c["customer"].lower()]
        if self.filter_status != "all":
            rows = [c for c in rows if c["status"] == self.filter_status]
        return [{"id": str(c["id"]), "customer": c["customer"], "type": c["type"],
                 "status": c["status"], "balance": f"{c['balance_due']:.2f}"} for c in rows]

    @rx.var
    def open_view(self) -> dict[str, str]:
        c = self.open_claim
        if not c:
            return {"id": "", "customer": "", "type": "", "status": "open", "filed": "", "balance": ""}
        return {"id": str(c["id"]), "customer": c["customer"], "type": c["type"],
                "status": c["status"], "filed": c["filed"], "balance": f"{c['balance_due']:.2f}"}

    @rx.var
    def steps_view(self) -> list[dict[str, str]]:
        out = []
        for i, s in enumerate(self.plan.get("steps", [])):
            cls = "stp cur" if i == self.step_idx else ("stp done" if i < self.step_idx else "stp")
            out.append({"n": str(i + 1), "why": s["why"], "cite": s["citation"]["doc"],
                        "g": "nav" if s.get("kind") == "nav" else f"grounded {s['grounding']:.2f}",
                        "ceil": "nav" if s.get("kind") == "nav" else s["autonomy_ceiling"],
                        "cls": cls})
        return out

    @rx.var
    def has_plan(self) -> bool:
        return bool(self.plan)

    @rx.var
    def copilot_ready(self) -> bool:
        return bool(self.plan) and self.step_idx < len(self.plan.get("steps", []))

    @rx.var
    def plan_chip(self) -> str:
        if not self.plan:
            return ""
        return f"{self.plan.get('plan_id','')} · {self.plan.get('compiler','')} · reg v{self.plan.get('registry_version','')}"

    @rx.var
    def progress_label(self) -> str:
        n = len(self.plan.get("steps", []))
        if not n:
            return ""
        return f"step {min(self.step_idx + 1, n)} / {n}"

    @rx.var
    def chunks_rows(self) -> list[dict[str, str]]:
        return [{"doc": h["doc"], "score": f"{h['score']:.2f}"} for h in self.chunks_view]

    @rx.var
    def esc_reason(self) -> str:
        return self.escalation.get("reason", "")

    @rx.var
    def esc_handoff(self) -> str:
        return self.escalation.get("handoff", "")

    @rx.var
    def rejected_text(self) -> str:
        return " · ".join(self.rejected)

    @rx.var
    def receipt_status(self) -> str:
        return self.receipt.get("status", "")

    @rx.var
    def receipt_after(self) -> str:
        return self.receipt.get("after", "")

    @rx.var
    def receipt_rows(self) -> list[dict[str, str]]:
        return [{"mark": "✓" if s["status"] == "ok" else "✕",
                 "cls": "rcp-mark " + s["status"], "why": s["why"]}
                for s in self.receipt.get("steps", [])]

    @rx.var
    def board_view(self) -> list[dict[str, str]]:
        out = []
        for t in self.board:
            patch = t.get("patch") or {}
            out.append({
                "goal": t.get("goal", ""), "status": t.get("status", ""),
                "detail": t.get("detail", ""),
                "patch_line": (f"PATCH  {patch.get('old_guide','')} → {patch.get('new_guide','')}"
                               if patch else ""),
                "evidence": " · ".join(patch.get("evidence", [])),
                "proof": t.get("proof", ""),
            })
        return out

    @rx.var
    def sab_active(self) -> bool:
        _ = self.sab_nonce
        return bool(sabotage.OVERRIDES)

    # ================= lifecycle =================
    @rx.event
    def on_load(self):
        if not self.claims:
            self.claims = copy.deepcopy(SEED_CLAIMS)

    # ================= dial & chrome =================
    @rx.event
    def set_mode(self, m: str):
        if self.executing or self.rehearsing:
            return
        self.mode = m
        self.done_msg = ""
        if self.has_plan and m in ("guide", "copilot") and self.step_idx < len(self.plan.get("steps", [])):
            self.spotlight = self.plan["steps"][self.step_idx]["selector"]
        else:
            self.spotlight = ""

    @rx.event
    def toggle_cmd(self):
        self.cmd_open = not self.cmd_open

    @rx.event
    def toggle_sentinel(self):
        self.sentinel_open = not self.sentinel_open

    @rx.event
    def clear_toast(self):
        self.toast = ""

    # ================= compile =================
    @rx.event(background=True)
    async def compile_goal(self, form_data: dict):
        goal = (form_data.get("goal") or "").strip()
        if not goal:
            return
        async with self:
            self.compiling = True
            self.plan = {}; self.escalation = {}; self.rejected = []
            self.chunks_view = []; self.receipt = {}; self.ticker = []
            self.done_msg = ""; self.step_idx = 0; self.spotlight = ""
            claims = _plain(self.claims)
        hits = await asyncio.to_thread(rag.retrieve, goal, 4)
        async with self:
            self.chunks_view = hits
        result = await asyncio.to_thread(planner.compile_plan, goal, claims)
        async with self:
            self.compiling = False
            self.cmd_open = False
            if "escalation" in result:
                self.escalation = result["escalation"]
            elif "rejected" in result:
                self.rejected = result["rejected"]
            else:
                self.plan = result
                store.save_plan(_plain(result))
                self._reset_meridian()
                self.step_idx = 0
                if self.mode in ("guide", "copilot"):
                    self.spotlight = result["steps"][0]["selector"]

    # ================= meridian actions (human OR executor) =================
    def _reset_meridian(self):
        self.route = "claims"; self.modal_open = False
        self.search = ""; self.filter_status = "all"
        self.refund_amount = ""; self.refund_reason = ""; self.refund_memo = ""

    def _open_claim_by_id(self, cid: int):
        claim = next((c for c in self.claims if c["id"] == int(cid)), None)
        if claim:
            self.open_claim = claim
            self.route = "claim"

    def _approve_refund(self):
        cid = self.open_claim.get("id")
        for c in self.claims:
            if c["id"] == cid:
                c["status"] = "refunded"; c["balance_due"] = 0.0
        self.open_claim = next(c for c in self.claims if c["id"] == cid)
        self.modal_open = False
        self.toast = f"Refund issued on claim #{cid}"

    def _field_satisfied(self, step: dict) -> bool:
        v = str(step.get("value") or "")
        cur = {"claims.search": self.search, "claims.refund.amount": self.refund_amount,
               "claims.refund.memo": self.refund_memo, "claims.notes.add": self.note_text,
               }.get(step["selector"], "")
        if step["selector"] == "claims.refund.memo":
            return len(cur.strip()) >= 10
        return cur.strip() == v.strip()

    def _advance_if_guided(self, cid: str):
        if self.executing or not self.has_plan or self.mode != "guide":
            return
        step = self.plan["steps"][self.step_idx] if self.step_idx < len(self.plan["steps"]) else None
        if not step or step["selector"] != cid:
            return
        if step["action"] == "fill" and not self._field_satisfied(step):
            return
        self._advance()

    def _advance(self):
        self.step_idx += 1
        steps = self.plan["steps"]
        if self.step_idx >= len(steps):
            self.spotlight = ""
            self.done_msg = "Plan complete — every step verified against policy."
        else:
            self.spotlight = steps[self.step_idx]["selector"]

    # -- human handlers (each mirrors what the executor can also do) --
    @rx.event
    def set_search(self, v: str):
        self.search = v; self._advance_if_guided("claims.search")

    @rx.event
    def set_filter(self, v: str):
        self.filter_status = v; self._advance_if_guided("claims.filter.status")

    @rx.event
    def open_row(self, cid: str):
        self._open_claim_by_id(int(cid)); self._advance_if_guided("claims.row.open")

    @rx.event
    def back_to_claims(self):
        self.route = "claims"

    @rx.event
    def start_refund(self):
        self.modal_open = True; self._advance_if_guided("claims.refund.start")

    @rx.event
    def cancel_refund(self):
        self.modal_open = False

    @rx.event
    def set_amount(self, v: str):
        self.refund_amount = v; self._advance_if_guided("claims.refund.amount")

    @rx.event
    def set_reason(self, v: str):
        self.refund_reason = v; self._advance_if_guided("claims.refund.reason_code")

    @rx.event
    def set_memo(self, v: str):
        self.refund_memo = v; self._advance_if_guided("claims.refund.memo")

    @rx.event
    def approve_refund(self):
        self._approve_refund(); self._advance_if_guided("claims.refund.approve")

    @rx.event
    def set_note(self, v: str):
        self.note_text = v

    @rx.event
    def add_note(self):
        self.note_text = ""; self.toast = "Note added"

    @rx.event
    def set_claim_status(self, v: str):
        if self.open_claim:
            for c in self.claims:
                if c["id"] == self.open_claim["id"]:
                    c["status"] = v
            self.open_claim = next(c for c in self.claims if c["id"] == self.open_claim["id"])

    @rx.event
    def open_docs(self):
        self.toast = "3 documents on file"

    # ================= executor (shared by copilot & autopilot) =================
    def _apply_step(self, step: dict):
        sid, val = step["selector"], step.get("value")
        if sid == "claims.search":
            self.search = str(val)
        elif sid == "claims.row.open":
            self._open_claim_by_id(int(val))
        elif sid == "claims.refund.start":
            self.modal_open = True
        elif sid == "claims.refund.amount":
            self.refund_amount = str(val)
        elif sid == "claims.refund.reason_code":
            self.refund_reason = str(val)
        elif sid == "claims.refund.memo":
            self.refund_memo = str(val)
        elif sid == "claims.refund.approve":
            self._approve_refund()
        elif sid == "claims.refund.cancel":
            self.modal_open = False
        elif sid == "claims.filter.status":
            self.filter_status = str(val)

    @rx.event
    def copilot_do_step(self):
        """Copilot: human confirms, Kerberos performs the current step."""
        if not self.has_plan or self.executing:
            return
        steps = self.plan["steps"]
        if self.step_idx >= len(steps):
            return
        step = steps[self.step_idx]
        self._apply_step(step)
        self.ticker = self.ticker + [
            f"▸ {self.step_idx+1}/{len(steps)} — {step['why']} · grounded {step['grounding']:.2f}"]
        self._advance()

    @rx.event
    def confirm_gate(self):
        self.awaiting = False
        self.await_msg = ""

    @rx.event(background=True)
    async def rehearse(self):
        async with self:
            if not self.has_plan or self.rehearsing:
                return
            self.rehearsing = True; self.receipt = {}
            plan = _plain(self.plan)
        try:
            result = await asyncio.to_thread(sandbox_replay, plan, BASE_URL)
        except Exception as e:
            result = {"status": "red", "steps": [], "after": "",
                      "failed_step": None, "goal": plan["goal"],
                      "plan_id": plan["plan_id"], "error": str(e)[:200]}
        async with self:
            self.rehearsing = False
            self.receipt = result

    @rx.event(background=True)
    async def autopilot_live(self):
        async with self:
            if not self.has_plan or self.executing:
                return
            self.executing = True
            self.ticker = []; self.done_msg = ""
            self._reset_meridian()
            self.step_idx = 0
            steps = _plain(self.plan["steps"])
        n = len(steps)
        for i, step in enumerate(steps):
            gate = step.get("autonomy_ceiling") != "autopilot"
            async with self:
                self.step_idx = i
                self.spotlight = step["selector"]
                if gate:
                    self.awaiting = True
                    self.await_msg = (f"Step {i+1} is weakly grounded ({step['grounding']:.2f}) — "
                                      "Kerberos will not act on it autonomously. Confirm to proceed.")
            if gate:
                while True:
                    await asyncio.sleep(0.25)
                    async with self:
                        if not self.awaiting:
                            break
            await asyncio.sleep(0.85)
            async with self:
                self._apply_step(step)
                self.ticker = self.ticker + [
                    f"▸ {i+1}/{n} — {step['why']} · grounded {step['grounding']:.2f}"]
        async with self:
            self.executing = False
            self.spotlight = ""
            self.step_idx = n
            self.done_msg = "Autopilot complete — rehearsed in sandbox, executed live."

    # ================= sentinel =================
    @rx.event(background=True)
    async def sentinel_run(self):
        from sentinel.replay import check_plan
        async with self:
            if self.sentinel_busy:
                return
            self.sentinel_busy = True
            self.board = []
        plans = await asyncio.to_thread(store.load_plans)
        for plan in plans:
            async with self:
                self.board = self.board + [{"plan_id": plan["plan_id"], "goal": plan["goal"],
                                            "status": "checking", "detail": "re-running in sandbox…",
                                            "patch": None, "proof": ""}]
            tile = await asyncio.to_thread(check_plan, plan, BASE_URL)
            async with self:
                self.board = self.board[:-1] + [tile]
                self.sab_nonce += 1   # registry may have been patched — refresh chips
        async with self:
            self.sentinel_busy = False
            if not plans:
                self.board = [{"plan_id": "—", "goal": "No stored plans yet — compile one first.",
                               "status": "empty", "detail": "", "patch": None, "proof": ""}]

    # ================= sabotage =================
    @rx.event
    def set_sab_target(self, v: str):
        self.sab_target = v

    @rx.event
    def set_sab_label(self, v: str):
        self.sab_label = v

    @rx.event
    def set_sab_move(self, v: bool):
        self.sab_move = v

    @rx.event
    def sabotage_apply(self):
        if not self.sab_label.strip():
            self.toast = "Type a new label first"
            return
        sabotage.apply(self.sab_target, self.sab_label.strip(),
                       self.sab_move and self.sab_target == "claims.refund.approve")
        self.sab_nonce += 1
        self.toast = f"Sabotage applied to {self.sab_target} — run Sentinel"

    @rx.event
    def sabotage_reset(self):
        sabotage.reset()
        self.sab_nonce += 1
        self.toast = "Sabotage reset"
