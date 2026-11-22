"""Uniqueness and signature-class statistics."""

from collections import Counter
from dataclasses import dataclass
from typing import Hashable


@dataclass(frozen=True)
class UniquenessStats:
    """Summary of how often each structural signature occurs."""

    unique_nodes: tuple[Hashable, ...]
    unique_signatures: tuple[tuple[int, int], ...]
    unique_count: int
    unique_fraction: float
    distinct_signatures: int
    largest_class_size: int
    class_size_histogram: dict[int, int]


def unique_stats(
    signature_by_node: dict[Hashable, tuple[int, int]],
) -> UniquenessStats:
    """Count unique signatures and summarize the sizes of all signature classes."""
    if not signature_by_node:
        raise ValueError("Cannot measure uniqueness for an empty graph.")

    frequencies = Counter(signature_by_node.values())
    unique_nodes = tuple(
        node for node, signature in signature_by_node.items()
        if frequencies[signature] == 1
    )
    unique_signatures = tuple(
        signature_by_node[node] for node in unique_nodes
    )
    class_size_histogram = dict(sorted(Counter(frequencies.values()).items()))
    return UniquenessStats(
        unique_nodes=unique_nodes,
        unique_signatures=unique_signatures,
        unique_count=len(unique_nodes),
        unique_fraction=len(unique_nodes) / len(signature_by_node),
        distinct_signatures=len(frequencies),
        largest_class_size=max(frequencies.values()),
        class_size_histogram=class_size_histogram,
    )
