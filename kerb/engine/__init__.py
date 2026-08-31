"""Kerb engine: retrieval, plan compilation, validation, and sandbox execution.

Import order matters to nothing here - every module in this package is usable
without the UI, which is what lets the sandbox runner and Sentinel reuse the
exact code path the live application takes.
"""
