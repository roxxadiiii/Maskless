"""Random edge replacement on an untouched copy of the anonymous graph."""

import random
from dataclasses import dataclass

import networkx as nx

from src.errors import InvariantError

Edge = tuple[str, str]


@dataclass(frozen=True)
class PerturbationResult:
    """Perturbed copy plus the exact edge changes and their sample size."""

    graph: nx.Graph
    edge_count: int
    replacement_count: int
    removed_edges: tuple[Edge, ...]
    added_edges: tuple[Edge, ...]


def replacement_count(edge_count: int, fraction: float) -> int:
    """Apply the SRS round-half-up rule without Python's banker's rounding."""
    if edge_count < 0:
        raise ValueError("Edge count cannot be negative.")
    if not 0 <= fraction < 1:
        raise ValueError("Perturbation fraction must be in [0, 1).")
    return int(fraction * edge_count + 0.5)


def _edge_fingerprint(graph: nx.Graph) -> tuple[Edge, ...]:
    """Return a canonical sorted edge tuple that detects source mutation."""
    return tuple(sorted(tuple(sorted(edge)) for edge in graph.edges()))


def perturb_graph(
    graph: nx.Graph,
    fraction: float,
    rng: random.Random,
) -> PerturbationResult:
    """Replace sampled existing edges with edges absent from the source graph."""
    if type(graph) is not nx.Graph:
        raise ValueError("Perturbation requires a simple undirected nx.Graph.")
    if not all(isinstance(node, str) for node in graph):
        raise ValueError("Perturbation requires string node identifiers.")
    if nx.number_of_selfloops(graph):
        raise ValueError("Source graph must not contain self-loops.")
    source_fingerprint = _edge_fingerprint(graph)
    edge_count = graph.number_of_edges()
    replacements = replacement_count(edge_count, fraction)
    existing_edges = list(source_fingerprint)
    absent_edges = sorted(
        tuple(sorted(edge)) for edge in nx.non_edges(graph)
    )
    if replacements > len(absent_edges):
        raise ValueError(
            f"Cannot add {replacements} edges: only {len(absent_edges)} "
            "non-edges exist in the original graph."
        )

    removed = tuple(rng.sample(existing_edges, replacements))
    added = tuple(rng.sample(absent_edges, replacements))
    perturbed = graph.copy()
    perturbed.remove_edges_from(removed)
    perturbed.add_edges_from(added)
    _check_postconditions(
        graph,
        perturbed,
        removed,
        added,
        replacements,
        source_fingerprint,
    )
    return PerturbationResult(
        graph=perturbed,
        edge_count=edge_count,
        replacement_count=replacements,
        removed_edges=removed,
        added_edges=added,
    )


def _check_postconditions(
    source: nx.Graph,
    perturbed: nx.Graph,
    removed: tuple[Edge, ...],
    added: tuple[Edge, ...],
    replacements: int,
    source_fingerprint: tuple[Edge, ...],
) -> None:
    """Fail loudly if copying or edge replacement violated any invariant."""
    if perturbed is source:
        raise InvariantError("Perturbation modified the source graph in place.")
    if type(perturbed) is not nx.Graph:
        raise InvariantError("Perturbed graph must be a simple undirected nx.Graph.")
    if perturbed.number_of_edges() != source.number_of_edges():
        raise InvariantError("Perturbation did not preserve the edge count.")
    if nx.number_of_selfloops(perturbed):
        raise InvariantError("Perturbed graph contains self-loops.")
    normalized_perturbed_edges = _edge_fingerprint(perturbed)
    if len(normalized_perturbed_edges) != len(set(normalized_perturbed_edges)):
        raise InvariantError("Perturbed graph contains duplicate edges.")
    if len(set(removed)) != replacements or len(set(added)) != replacements:
        raise InvariantError("Perturbation edge samples contain duplicates.")
    if any(not source.has_edge(*edge) for edge in removed):
        raise InvariantError("A removed edge did not exist in the source graph.")
    if any(source.has_edge(*edge) for edge in added):
        raise InvariantError("An added edge existed in the original graph.")
    if set(removed).intersection(added):
        raise InvariantError("Removed and added edge sets overlap.")
    source_edges = set(source_fingerprint)
    perturbed_edges = set(normalized_perturbed_edges)
    if len(source_edges.symmetric_difference(perturbed_edges)) != 2 * replacements:
        raise InvariantError("Perturbation changed an unexpected number of edges.")
    if set(source) != set(perturbed):
        raise InvariantError("Perturbation changed the node set.")
    if _edge_fingerprint(source) != source_fingerprint:
        raise InvariantError("Perturbation modified the source graph.")
