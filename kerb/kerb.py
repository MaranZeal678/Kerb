"""Kerb shell: trust dial + command bar + plan rail + Sentinel drawer (spec §8)."""

import reflex as rx

from .meridian.app import meridian_view
from .meridian.data import SUGGESTED_GOALS
from .state import KState

MODES = [("Guide", "guide"), ("Copilot", "copilot"), ("Autopilot", "autopilot")]
SAB_TARGETS = ["claims.refund.approve", "claims.refund.start", "claims.refund.reason_code",
               "claims.refund.memo", "claims.refund.amount", "claims.row.open", "claims.search"]


def topbar() -> rx.Component:
    return rx.el.header(
        rx.el.div(rx.el.span("KERB", class_name="k-brand"),
                  rx.el.span("one plan · three levels of trust", class_name="k-brand-sub"),
                  class_name="k-brand-wrap"),
        rx.el.div(
            *[rx.el.button(label,
                           on_click=KState.set_mode(value),
                           class_name=rx.cond(KState.mode == value, f"dial-btn {value} on", f"dial-btn {value}"))
              for label, value in MODES],
            class_name="dial",
        ),
        rx.el.div(
            rx.cond(KState.has_plan,
                    rx.el.span(KState.plan_chip, class_name="plan-chip mono"),
                    rx.el.span("no plan", class_name="plan-chip mono dim")),
            rx.el.button("⌘K  Ask", on_click=KState.toggle_cmd, class_name="k-btn"),
            rx.el.button(rx.cond(KState.sab_active, "Sentinel ●", "Sentinel"),
                         on_click=KState.toggle_sentinel,
                         class_name=rx.cond(KState.sentinel_open, "k-btn on", "k-btn")),
            class_name="k-right",
        ),
        class_name="k-topbar",
    )


def cmd_bar() -> rx.Component:
    return rx.cond(
        KState.cmd_open,
        rx.el.div(
            rx.el.div(
                rx.el.form(
                    rx.el.input(placeholder='Ask for an outcome — "Issue a refund for claim #4821"',
                                name="goal", auto_focus=True, class_name="cmd-input"),
                    on_submit=KState.compile_goal, class_name="cmd-form",
                ),
                rx.el.div(
                    *[rx.el.button(g, on_click=KState.compile_goal({"goal": g}), class_name="cmd-sug")
                      for g in SUGGESTED_GOALS],
                    class_name="cmd-sugs",
                ),
                class_name="cmd-box",
            ),
            class_name="cmd-wrap",
        ),
        rx.fragment(),
    )


def step_card(s: rx.Var) -> rx.Component:
    return rx.el.div(
        rx.el.div(
            rx.el.span(s["n"], class_name="stp-n mono"),
            rx.el.span(s["why"], class_name="stp-why"),
            class_name="stp-top",
        ),
        rx.el.div(
            rx.el.span(s["cite"], class_name="chip cite"),
            rx.el.span(s["g"], class_name="chip g-" + s["ceil"]),
            class_name="stp-chips",
        ),
        class_name=s["cls"],
    )


def escalation_card() -> rx.Component:
    return rx.el.div(
        rx.el.span("ESCALATION — Kerb will not act here", class_name="esc-title"),
        rx.el.p(KState.esc_reason, class_name="esc-body"),
        rx.el.p(KState.esc_handoff, class_name="esc-hand mono"),
        class_name="esc-card",
    )


def receipt_panel() -> rx.Component:
    return rx.el.div(
        rx.el.span(rx.cond(KState.receipt_status == "green",
                           "SANDBOX RECEIPT — rehearsal clean",
                           "SANDBOX RECEIPT — rehearsal FAILED"),
                   class_name="rcp-title mono"),
        rx.foreach(KState.receipt_rows,
                   lambda s: rx.el.div(
                       rx.el.span(s["mark"], class_name=s["cls"]),
                       rx.el.span(s["why"], class_name="rcp-why"),
                       class_name="rcp-row")),
        rx.cond(KState.receipt_status == "green",
                rx.el.div(
                    rx.el.span("after: claim status → ", KState.receipt_after, class_name="rcp-diff mono"),
                    rx.el.button("Run live", on_click=KState.autopilot_live, class_name="k-btn go"),
                    class_name="rcp-foot"),
                rx.el.span("The live run is blocked until a rehearsal passes.", class_name="rcp-blocked")),
        class_name="rcp",
    )


def rail() -> rx.Component:
    return rx.el.aside(
        rx.cond(KState.compiling,
                rx.el.div(
                    rx.el.span("compiling — retrieving policy…", class_name="rail-label mono pulse"),
                    rx.foreach(KState.chunks_rows,
                               lambda h: rx.el.div(
                                   rx.el.span(h["doc"], class_name="chip cite"),
                                   rx.el.span(h["score"], class_name="chip score mono"),
                                   class_name="chunk-row")),
                    class_name="rail-sec"),
                rx.fragment()),
        rx.cond(KState.esc_reason != "", escalation_card(), rx.fragment()),
        rx.cond(KState.rejected_text != "",
                rx.el.div(rx.el.span("PLAN REJECTED BY VALIDATOR", class_name="esc-title"),
                          rx.el.p(KState.rejected_text, class_name="esc-body mono"),
                          class_name="esc-card"),
                rx.fragment()),
        rx.cond(
            KState.has_plan,
            rx.el.div(
                rx.el.div(rx.el.span("GUIDE PLAN", class_name="rail-label mono"),
                          rx.el.span(KState.progress_label, class_name="rail-label mono dim"),
                          class_name="rail-head"),
                rx.foreach(KState.steps_view, step_card),
                rx.cond((KState.mode == "copilot") & KState.copilot_ready,
                        rx.el.button("Confirm & do this step", on_click=KState.copilot_do_step,
                                     class_name="k-btn amber wide"),
                        rx.fragment()),
                rx.cond(KState.mode == "autopilot",
                        rx.el.div(
                            rx.cond(KState.rehearsing,
                                    rx.el.span("rehearsing in sandbox…", class_name="rail-label mono pulse"),
                                    rx.el.button("Rehearse in sandbox", on_click=KState.rehearse,
                                                 class_name="k-btn violet wide")),
                            rx.cond(KState.receipt_status != "", receipt_panel(), rx.fragment()),
                            class_name="rail-sec"),
                        rx.fragment()),
                rx.cond(KState.awaiting,
                        rx.el.div(rx.el.p(KState.await_msg, class_name="gate-msg"),
                                  rx.el.button("Confirm — proceed", on_click=KState.confirm_gate,
                                               class_name="k-btn amber wide"),
                                  class_name="gate"),
                        rx.fragment()),
                rx.cond(KState.done_msg != "",
                        rx.el.div(KState.done_msg, class_name="done"), rx.fragment()),
                rx.el.div(rx.foreach(KState.ticker, lambda t: rx.el.div(t, class_name="tick mono")),
                          class_name="ticker"),
                class_name="rail-sec",
            ),
            rx.cond(KState.compiling | (KState.esc_reason != "") | (KState.rejected_text != ""),
                    rx.fragment(),
                    rx.el.div(
                        rx.el.span("KERB", class_name="rail-label mono"),
                        rx.el.p("Ask for an outcome with ⌘K Ask. The dial sets how much Kerb does: "
                                "Guide teaches, Copilot acts with you, Autopilot rehearses in a sandbox "
                                "and then does it.", class_name="rail-intro"),
                        class_name="rail-sec")),
        ),
        class_name="rail",
    )


def tile_view(t: rx.Var) -> rx.Component:
    return rx.el.div(
        rx.el.div(rx.el.span(class_name="lamp " + t["status"]),
                  rx.el.span(t["goal"], class_name="tile-goal"),
                  rx.el.span(t["status"], class_name="tile-status mono"),
                  class_name="tile-top"),
        rx.el.p(t["detail"], class_name="tile-detail"),
        rx.cond(t["patch_line"] != "",
                rx.el.div(
                    rx.el.span(t["patch_line"], class_name="patch-line mono"),
                    rx.el.span(t["evidence"], class_name="chip evid"),
                    rx.el.span(t["proof"], class_name="patch-proof mono"),
                    class_name="patch"),
                rx.fragment()),
        class_name="tile",
    )


def sentinel_drawer() -> rx.Component:
    return rx.cond(
        KState.sentinel_open,
        rx.el.aside(
            rx.el.div(rx.el.span("SENTINEL — verification board", class_name="rail-label mono"),
                      rx.cond(KState.sentinel_busy,
                              rx.el.span("re-running guides in sandbox…", class_name="rail-label mono pulse"),
                              rx.el.button("Run Sentinel", on_click=KState.sentinel_run, class_name="k-btn go")),
                      class_name="sen-head"),
            rx.foreach(KState.board_view, tile_view),
            rx.el.div(
                rx.el.span("SABOTAGE PANEL — break it yourself", class_name="rail-label mono"),
                rx.el.select(*[rx.el.option(t, value=t) for t in SAB_TARGETS],
                             value=KState.sab_target, on_change=KState.set_sab_target, class_name="m-select"),
                rx.el.input(placeholder="New label — e.g. Release Funds",
                            value=KState.sab_label, on_change=KState.set_sab_label, class_name="m-input"),
                rx.el.label(
                    rx.el.input(type="checkbox", checked=KState.sab_move, on_change=KState.set_sab_move),
                    rx.el.span("  also move it (approve button only)"), class_name="sab-move"),
                rx.el.div(
                    rx.el.button("Apply sabotage", on_click=KState.sabotage_apply, class_name="k-btn red"),
                    rx.el.button("Reset", on_click=KState.sabotage_reset, class_name="k-btn"),
                    class_name="sab-foot"),
                class_name="sab",
            ),
            class_name="sentinel",
        ),
        rx.fragment(),
    )


def index() -> rx.Component:
    return rx.el.div(
        topbar(),
        rx.el.div(meridian_view(), rail(), class_name="k-body"),
        sentinel_drawer(),
        cmd_bar(),
        rx.cond(KState.executing,
                rx.el.div(rx.el.span("AUTOPILOT — input frozen", class_name="scrim-tag mono"),
                          class_name="scrim-exec"),
                rx.fragment()),
        rx.cond((KState.spotlight != "") & ~KState.executing,
                rx.el.div(class_name="scrim-soft"), rx.fragment()),
        rx.cond(KState.toast != "",
                rx.el.div(KState.toast, on_click=KState.clear_toast, class_name="toast"),
                rx.fragment()),
        custom_attrs={"data-mode": KState.mode},
        class_name="app",
    )


app = rx.App(stylesheets=["/styles.css"])
app.add_page(index, route="/", title="Kerb", on_load=KState.on_load)
