"""Shared test helpers."""

from pathlib import Path

EXAMPLES = Path(__file__).parent / "examples"


def example(name: str) -> bytes:
    """Read one of the documented examples in ``tests/examples``."""
    return (EXAMPLES / name).read_bytes()
