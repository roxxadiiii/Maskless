"""Configuration and command-line parsing for the project."""

from __future__ import annotations

import argparse
from dataclasses import dataclass
from pathlib import Path
from typing import Optional, Sequence

SUPPORTED_MODELS = ("powerlaw_cluster", "barabasi_albert")


@dataclass(frozen=True)
class Config:
    """All tunable settings for one reproducible experiment."""

    n: int = 100
    model: str = "powerlaw_cluster"
    m_attach: int = 3
    p_triad: float = 0.5
    master_seed: int = 42
    rewire_fraction: float = 0.10
    top_k: int = 5
    robust_runs: int = 200
    out_dir: Path = Path("results")
    no_plots: bool = False

    @property
    def seeds(self) -> dict[str, int]:
        """Return deterministic, stage-specific seeds derived from the master."""
        return {
            "master": self.master_seed,
            "names": self.master_seed + 1,
            "anon": self.master_seed + 2,
            "perturb": self.master_seed + 3,
            "robust_base": self.master_seed + 1000,
        }

    def validate(self) -> None:
        """Reject invalid configuration before any work or file writes."""
        if self.n < 3:
            raise ValueError("N must be at least 3.")
        if self.model not in SUPPORTED_MODELS:
            raise ValueError(f"Unsupported model: {self.model!r}.")
        if not 1 <= self.m_attach < self.n:
            raise ValueError("m must be at least 1 and less than N.")
        if not 0 <= self.p_triad <= 1:
            raise ValueError("p must be between 0 and 1, inclusive.")
        if not 0 < self.rewire_fraction < 1:
            raise ValueError("rewire fraction must be greater than 0 and less than 1.")
        if not 1 <= self.top_k <= self.n:
            raise ValueError("top-k must be at least 1 and no greater than N.")
        if self.robust_runs < 1:
            raise ValueError("robust-runs must be at least 1.")


class _ArgumentParser(argparse.ArgumentParser):
    """Make command-line validation use the documented validation exit code."""

    def error(self, message: str) -> None:
        """Raise ValueError so CLI validation maps to the documented exit code."""
        raise ValueError(message)


def parse_config(argv: Optional[Sequence[str]] = None) -> Config:
    """Parse CLI overrides, validate them and return the effective config."""
    parser = _ArgumentParser(
        description="Generate a synthetic network for the Maskless privacy study."
    )
    parser.add_argument("--n", type=int, default=100)
    parser.add_argument("--model", choices=SUPPORTED_MODELS, default="powerlaw_cluster")
    parser.add_argument("--m", type=int, default=3)
    parser.add_argument("--p", type=float, default=0.5)
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--rewire", type=float, default=0.10)
    parser.add_argument("--topk", type=int, default=5)
    parser.add_argument("--robust-runs", type=int, default=200)
    parser.add_argument("--out", type=Path, default=Path("results"))
    parser.add_argument("--no-plots", action="store_true")
    args = parser.parse_args(argv)

    config = Config(
        n=args.n,
        model=args.model,
        m_attach=args.m,
        p_triad=args.p,
        master_seed=args.seed,
        rewire_fraction=args.rewire,
        top_k=args.topk,
        robust_runs=args.robust_runs,
        out_dir=args.out,
        no_plots=args.no_plots,
    )
    config.validate()
    return config
