"""Seeded Meridian data — engineered so every demo beat fires deterministically (spec §2)."""

SEED_CLAIMS = [
    {"id": 4821, "customer": "Dana Whitfield",  "type": "Auto — collision",   "status": "open",     "balance_due": 612.50, "filed": "2026-08-11"},
    {"id": 3377, "customer": "Miguel Ortega",   "type": "Home — water damage","status": "open",     "balance_due": 180.00, "filed": "2026-08-14"},
    {"id": 5150, "customer": "Priya Raman",     "type": "Auto — theft",       "status": "disputed", "balance_due": 940.00, "filed": "2026-07-30"},
    {"id": 4102, "customer": "Sam Becker",      "type": "Home — fire",        "status": "approved", "balance_due": 0.00,   "filed": "2026-08-02"},
    {"id": 4655, "customer": "Lena Kovacs",     "type": "Auto — glass",       "status": "open",     "balance_due": 320.75, "filed": "2026-08-18"},
    {"id": 3910, "customer": "Owen Carty",      "type": "Renters — theft",    "status": "open",     "balance_due": 89.99,  "filed": "2026-08-20"},
    {"id": 5033, "customer": "Ines Duarte",     "type": "Auto — collision",   "status": "approved", "balance_due": 1450.00,"filed": "2026-08-05"},
    {"id": 2748, "customer": "Theo Lindqvist",  "type": "Home — storm",       "status": "closed",   "balance_due": 0.00,   "filed": "2026-06-19"},
    {"id": 4477, "customer": "Ruth Adeyemi",    "type": "Auto — liability",   "status": "open",     "balance_due": 505.10, "filed": "2026-08-21"},
    {"id": 3560, "customer": "Marco Bellini",   "type": "Home — plumbing",    "status": "closed",   "balance_due": 0.00,   "filed": "2026-07-08"},
    {"id": 4990, "customer": "Aiko Tanaka",     "type": "Renters — damage",   "status": "open",     "balance_due": 260.40, "filed": "2026-08-24"},
    {"id": 3021, "customer": "Nadia Osei",      "type": "Auto — hail",        "status": "approved", "balance_due": 0.00,   "filed": "2026-07-22"},
]

REASON_CODES = ["RC-01", "RC-02", "RC-03", "RC-04", "RC-05", "RC-06",
                "RC-07", "RC-08", "RC-09", "RC-10", "RC-11", "RC-12"]

STATUSES = ["all", "open", "approved", "disputed", "closed"]

SUGGESTED_GOALS = [
    "Issue a refund for claim #4821",
    "Issue a refund for claim #3377",
    "Issue a refund for claim #5150",
]
