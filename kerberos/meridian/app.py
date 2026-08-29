"""Meridian — the instrumented demo target: a mock claims/refund back-office portal.

Every interactive control carries custom_attrs={"data-guide": "<registry id>"} so the
registry and the app are generated from the same constants. The sabotage switch
(KERBEROS_SABOTAGE_TARGET) renames/moves one control to demo Sentinel self-healing.

STATUS: scaffold. Build in Tier 1.1 — claims list, claim detail, refund flow (~12 controls).
"""
