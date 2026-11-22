"""Relabel named graph nodes with anonymous identifiers."""

import random
from typing import Any

import networkx as nx

from src.errors import InvariantError


def make_mapping(graph: nx.Graph, rng: random.Random) -> dict[str, str]:
    """Create a seeded random bijection from names to zero-padded user IDs."""
    names = sorted(graph.nodes())
    if not all(isinstance(name, str) for name in names):
        raise ValueError("Anonymisation requires string node labels.")
    width = max(3, len(str(len(names))))
    identifiers = [f"U{index:0{width}d}" for index in range(1, len(names) + 1)]
    rng.shuffle(identifiers)
    return dict(zip(names, identifiers))


def anonymize_graph(
    graph: nx.Graph, rng: random.Random
) -> tuple[nx.Graph, dict[str, str]]:
    """Return a copied graph with anonymous labels and its private mapping."""
    mapping = make_mapping(graph, rng)
    anonymized = nx.relabel_nodes(graph, mapping, copy=True)
    if len(mapping) != graph.number_of_nodes() or len(set(mapping.values())) != len(mapping):
        raise InvariantError("Anonymisation mapping is not a bijection.")
    check_leakage(anonymized, set(mapping))
    return anonymized, mapping


def _contains_name(value: Any, names: set[str]) -> bool:
    if isinstance(value, str):
        return any(name in value for name in names)
    if isinstance(value, dict):
        return any(
            _contains_name(key, names) or _contains_name(item, names)
            for key, item in value.items()
        )
    if isinstance(value, (list, tuple, set)):
        return any(_contains_name(item, names) for item in value)
    return False


def check_leakage(graph: nx.Graph, original_names: set[str]) -> None:
    """Reject original names in anonymized labels or graph attributes."""
    if original_names.intersection(graph.nodes()):
        raise InvariantError("Original names remain among anonymized node labels.")
    attribute_groups = [
        graph.graph,
        *(data for _, data in graph.nodes(data=True)),
        *(data for _, _, data in graph.edges(data=True)),
    ]
    if any(_contains_name(attributes, original_names) for attributes in attribute_groups):
        raise InvariantError("Original names remain in anonymized graph attributes.")
