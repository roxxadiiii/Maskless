"""Repeated perturbation runs on one fixed anonymous graph."""

import random
from statistics import fmean, pstdev
from typing import Any, Sequence

import networkx as nx

from src.compare import compare_graphs
from src.perturb import perturb_graph


def _percentile(sorted_values: Sequence[float], percentile: float) -> float:
    """Interpolate linearly between ordered observations using type-7 positions."""
    if not sorted_values:
        raise ValueError("At least one observation is required.")
    if not 0 <= percentile <= 100:
        raise ValueError("Percentile must be between 0 and 100.")
    position = (len(sorted_values) - 1) * percentile / 100
    lower = int(position)
    upper = min(lower + 1, len(sorted_values) - 1)
    fraction = position - lower
    return sorted_values[lower] + fraction * (
        sorted_values[upper] - sorted_values[lower]
    )


def _summarize(values: list[float]) -> dict[str, float]:
    """Describe a complete run set with population spread and linear percentiles."""
    ordered = sorted(values)
    return {
        "mean": fmean(ordered),
        "standard_deviation": pstdev(ordered),
        "minimum": ordered[0],
        "percentile_05": _percentile(ordered, 5),
        "percentile_95": _percentile(ordered, 95),
        "maximum": ordered[-1],
    }


def run_robustness(
    graph: nx.Graph,
    fraction: float,
    runs: int,
    top_k: int,
    seed_start: int,
) -> dict[str, Any]:
    """Repeat perturbation and comparison while keeping the base graph fixed."""
    if runs < 1:
        raise ValueError("Robustness runs must be at least 1.")

    samples = []
    for index in range(runs):
        seed = seed_start + index
        perturbation = perturb_graph(graph, fraction, random.Random(seed))
        comparison = compare_graphs(graph, perturbation.graph, top_k)
        samples.append(
            {
                "index": index,
                "seed": seed,
                "unique_fraction_after": comparison["unique"]["after"]["fraction"],
                "average_clustering_after": comparison["clustering"]["after"],
                "top_k_overlap": comparison["ranking"]["overlap_count"],
            }
        )

    return {
        "runs": runs,
        "seed_start": seed_start,
        "seed_end": seed_start + runs - 1,
        "seed_sequence": "seed_start + i, where i ranges from 0 to runs - 1",
        "standard_deviation_method": "population standard deviation (ddof=0)",
        "percentile_method": "linear interpolation (type 7)",
        "top_k": top_k,
        "summaries": {
            "unique_fraction_after": _summarize(
                [sample["unique_fraction_after"] for sample in samples]
            ),
            "average_clustering_after": _summarize(
                [sample["average_clustering_after"] for sample in samples]
            ),
            "top_k_overlap": _summarize(
                [sample["top_k_overlap"] for sample in samples]
            ),
        },
        "samples": samples,
    }
