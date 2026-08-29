"""Kerberos app shell: autonomy dial + guidance overlay + Meridian demo app.

STATUS: scaffold. Tier 1.1 / 1.5 / 1.7.
"""

import reflex as rx

from .state import KerberosState


def autonomy_dial() -> rx.Component:
    """The toggle. One state var; the whole surface re-projects when it changes."""
    return rx.hstack(
        *[
            rx.button(
                label,
                on_click=KerberosState.set_mode(value),
                variant=rx.cond(KerberosState.mode == value, "solid", "ghost"),
            )
            for label, value in [("Guide", "guide"), ("Copilot", "copilot"), ("Autopilot", "autopilot")]
        ],
    )


def index() -> rx.Component:
    return rx.vstack(
        rx.heading("Kerberos"),
        autonomy_dial(),
        rx.text("Meridian demo app + guidance overlay mount here (Tier 1)."),
    )


app = rx.App()
app.add_page(index)
