"""Meridian — the instrumented demo stage (spec §2). Built on rx.el for stable,
fully-styleable primitives. Every registered control carries a dynamic data-guide
attribute (sabotage-aware) and the spotlight class hook."""

import reflex as rx

from ..state import KState
from .data import REASON_CODES, STATUSES


def _cls(cid: str, base: str = "ctl"):
    return rx.cond(KState.spotlight == cid, base + " hot", base)


def _g(cid: str) -> dict:
    return {"data-guide": KState.ui[cid + ".g"]}


def claims_screen() -> rx.Component:
    return rx.el.section(
        rx.el.div(
            rx.el.h2("Claims", class_name="m-title"),
            rx.el.div(
                rx.el.input(
                    placeholder="Search claim # or customer…",
                    value=KState.search, on_change=KState.set_search,
                    custom_attrs=_g("claims.search"), class_name=_cls("claims.search", "ctl m-input"),
                ),
                rx.el.select(
                    *[rx.el.option(s, value=s) for s in STATUSES],
                    value=KState.filter_status, on_change=KState.set_filter,
                    custom_attrs=_g("claims.filter.status"),
                    class_name=_cls("claims.filter.status", "ctl m-select"),
                ),
                class_name="m-toolbar",
            ),
            class_name="m-head",
        ),
        rx.el.div(
            rx.el.div(
                rx.el.span("Claim"), rx.el.span("Customer"), rx.el.span("Type"),
                rx.el.span("Status"), rx.el.span("Balance due"), rx.el.span(""),
                class_name="m-row m-row-head",
            ),
            rx.foreach(
                KState.claims_view,
                lambda c: rx.el.div(
                    rx.el.span("#", c["id"], class_name="mono"),
                    rx.el.span(c["customer"]),
                    rx.el.span(c["type"], class_name="dim"),
                    rx.el.span(c["status"], class_name="pill st-" + c["status"]),
                    rx.el.span("$", c["balance"], class_name="mono"),
                    rx.el.button(
                        KState.ui["claims.row.open.label"],
                        on_click=KState.open_row(c["id"]),
                        custom_attrs=_g("claims.row.open"),
                        class_name=_cls("claims.row.open", "ctl m-btn ghost"),
                    ),
                    class_name="m-row",
                ),
            ),
            class_name="m-table",
        ),
        custom_attrs={"data-region": "claims-list"},
        class_name="m-screen",
    )


def _approve_button(extra: str = "") -> rx.Component:
    return rx.el.button(
        KState.ui["claims.refund.approve.label"],
        on_click=KState.approve_refund,
        custom_attrs=_g("claims.refund.approve"),
        class_name=_cls("claims.refund.approve", "ctl m-btn primary " + extra),
    )


def refund_modal() -> rx.Component:
    return rx.cond(
        KState.modal_open,
        rx.el.div(
            rx.el.div(
                rx.el.div(
                    rx.el.h3("Issue refund", class_name="m-title sm"),
                    rx.cond(KState.ui["claims.refund.approve.moved"] == "1",
                            _approve_button("moved"), rx.fragment()),
                    class_name="m-modal-head",
                ),
                rx.el.label("Refund amount", class_name="m-label"),
                rx.el.input(
                    placeholder="0.00", value=KState.refund_amount, on_change=KState.set_amount,
                    custom_attrs=_g("claims.refund.amount"),
                    class_name=_cls("claims.refund.amount", "ctl m-input"),
                ),
                rx.el.label("Reason code", class_name="m-label"),
                rx.el.select(
                    rx.el.option("— select —", value=""),
                    *[rx.el.option(c, value=c) for c in REASON_CODES],
                    value=KState.refund_reason, on_change=KState.set_reason,
                    custom_attrs=_g("claims.refund.reason_code"),
                    class_name=_cls("claims.refund.reason_code", "ctl m-select"),
                ),
                rx.el.label("Supervisor memo", class_name="m-label"),
                rx.el.textarea(
                    placeholder="Brief written note…", value=KState.refund_memo,
                    on_change=KState.set_memo, custom_attrs=_g("claims.refund.memo"),
                    class_name=_cls("claims.refund.memo", "ctl m-textarea"),
                ),
                rx.el.div(
                    rx.el.button(
                        KState.ui["claims.refund.cancel.label"], on_click=KState.cancel_refund,
                        custom_attrs=_g("claims.refund.cancel"),
                        class_name=_cls("claims.refund.cancel", "ctl m-btn ghost"),
                    ),
                    rx.cond(KState.ui["claims.refund.approve.moved"] == "0",
                            _approve_button(), rx.fragment()),
                    class_name="m-modal-foot",
                ),
                custom_attrs={"data-region": "refund-modal"},
                class_name="m-modal",
            ),
            class_name="m-modal-wrap",
        ),
        rx.fragment(),
    )


def claim_screen() -> rx.Component:
    return rx.el.section(
        rx.el.button("← All claims", on_click=KState.back_to_claims, class_name="m-btn link"),
        rx.el.div(
            rx.el.div(
                rx.el.h2("Claim #", KState.open_view["id"], class_name="m-title"),
                rx.el.span(KState.open_view["status"],
                           custom_attrs={"data-field": "claim-status"},
                           class_name="pill st-" + KState.open_view["status"]),
                class_name="m-claim-head",
            ),
            rx.el.div(
                rx.el.div(rx.el.span("Customer", class_name="m-label"), rx.el.span(KState.open_view["customer"])),
                rx.el.div(rx.el.span("Type", class_name="m-label"), rx.el.span(KState.open_view["type"])),
                rx.el.div(rx.el.span("Filed", class_name="m-label"), rx.el.span(KState.open_view["filed"], class_name="mono")),
                rx.el.div(rx.el.span("Balance due", class_name="m-label"),
                          rx.el.span("$", KState.open_view["balance"], class_name="mono big")),
                class_name="m-grid",
            ),
            rx.el.div(
                rx.el.button(
                    KState.ui["claims.refund.start.label"], on_click=KState.start_refund,
                    custom_attrs=_g("claims.refund.start"),
                    class_name=_cls("claims.refund.start", "ctl m-btn primary"),
                ),
                rx.el.button(
                    KState.ui["claims.docs.open.label"], on_click=KState.open_docs,
                    custom_attrs=_g("claims.docs.open"),
                    class_name=_cls("claims.docs.open", "ctl m-btn ghost"),
                ),
                rx.el.select(
                    *[rx.el.option(s, value=s) for s in ["open", "approved", "disputed", "closed", "refunded"]],
                    value=KState.open_view["status"], on_change=KState.set_claim_status,
                    custom_attrs=_g("claims.status.set"),
                    class_name=_cls("claims.status.set", "ctl m-select"),
                ),
                class_name="m-actions",
            ),
            rx.el.div(
                rx.el.input(
                    placeholder="Add a note…", value=KState.note_text, on_change=KState.set_note,
                    custom_attrs=_g("claims.notes.add"),
                    class_name=_cls("claims.notes.add", "ctl m-input"),
                ),
                rx.el.button("Add", on_click=KState.add_note, class_name="m-btn ghost"),
                class_name="m-notes",
            ),
            class_name="m-card",
        ),
        refund_modal(),
        custom_attrs={"data-region": "claim-detail"},
        class_name="m-screen",
    )


def meridian_view() -> rx.Component:
    return rx.el.main(
        rx.el.div(
            rx.el.span("MERIDIAN", class_name="m-brand"),
            rx.el.span("Claims Operations", class_name="m-brand-sub"),
            class_name="m-topline",
        ),
        rx.cond(KState.route == "claims", claims_screen(), claim_screen()),
        class_name="meridian",
    )
