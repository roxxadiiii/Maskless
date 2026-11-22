"""Fictional node-label generation."""

import random


_FIRST_NAMES = (
    "Aarav", "Diya", "Kabir", "Meera", "Rohan",
    "Sana", "Vikram", "Isha", "Neel", "Tara",
)
_LAST_NAMES = (
    "Sharma", "Verma", "Khan", "Singh", "Das",
    "Iyer", "Mishra", "Roy", "Nair", "Gupta",
)


def build_names(n: int, rng: random.Random) -> list[str]:
    """Sample unique fictional full names without replacement."""
    pool = [f"{first} {last}" for first in _FIRST_NAMES for last in _LAST_NAMES]
    if n < 0:
        raise ValueError("N cannot be negative.")
    if n > len(pool):
        raise ValueError(f"Name pool supports at most {len(pool)} users; got {n}.")
    return rng.sample(pool, n)
