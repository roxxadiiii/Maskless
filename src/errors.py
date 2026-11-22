"""Shared exceptions for invalid configuration and failed invariants."""


class InvariantError(RuntimeError):
    """Raised when an internal graph invariant is violated."""
