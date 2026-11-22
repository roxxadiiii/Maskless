from collections import Counter
import random

import networkx as nx
import pytest

from src.perturb import perturb_graph, replacement_count


@pytest.mark.parametrize(("edge_count", "expected"), [(291, 29), (295, 30)])
def test_replacement_count_uses_round_half_up(edge_count, expected):
    assert replacement_count(edge_count, 0.10) == expected


def test_perturbation_preserves_count_and_source_and_adds_original_non_edges():
    graph = nx.powerlaw_cluster_graph(100, 3, 0.5, seed=42)
    graph = nx.relabel_nodes(graph, {node: f"U{node:03d}" for node in graph})
    original_edges = {frozenset(edge) for edge in graph.edges()}
    original_nodes = set(graph)

    result = perturb_graph(graph, 0.10, random.Random(45))
    added = set(result.added_edges)
    removed = set(result.removed_edges)
    perturbed_edges = {frozenset(edge) for edge in result.graph.edges()}

    assert result.edge_count == graph.number_of_edges()
    assert result.replacement_count == int(0.10 * graph.number_of_edges() + 0.5)
    assert type(result.graph) is nx.Graph
    assert result.graph.number_of_edges() == graph.number_of_edges()
    assert set(result.graph) == original_nodes
    assert nx.number_of_selfloops(result.graph) == 0
    assert len(perturbed_edges) == result.graph.number_of_edges()
    assert len(added) == len(removed) == result.replacement_count
    assert all(not graph.has_edge(*edge) for edge in added)
    assert all(graph.has_edge(*edge) for edge in removed)
    assert not (added & removed)
    assert len(original_edges.symmetric_difference(perturbed_edges)) == 2 * result.replacement_count
    assert original_edges == {frozenset(edge) for edge in graph.edges()}


def test_perturbation_is_reproducible_and_zero_fraction_is_identity():
    graph = nx.path_graph(["U001", "U002", "U003", "U004"])
    first = perturb_graph(graph, 0.25, random.Random(8))
    second = perturb_graph(graph, 0.25, random.Random(8))
    assert first.removed_edges == second.removed_edges
    assert first.added_edges == second.added_edges

    identity = perturb_graph(graph, 0, random.Random(8))
    assert identity.replacement_count == 0
    assert set(identity.graph.edges()) == set(graph.edges())
    assert identity.removed_edges == identity.added_edges == ()


def test_perturbation_rejects_unavailable_original_non_edges():
    graph = nx.complete_graph(["U001", "U002", "U003"])
    with pytest.raises(ValueError, match="non-edges exist"):
        perturb_graph(graph, 0.5, random.Random(2))


def test_edge_removal_sampling_is_approximately_uniform():
    graph = nx.cycle_graph([f"U{node:03d}" for node in range(6)])
    removed_counts = Counter(
        perturb_graph(graph, 0.1, random.Random(seed)).removed_edges[0]
        for seed in range(6000)
    )

    assert len(removed_counts) == graph.number_of_edges()
    assert max(removed_counts.values()) - min(removed_counts.values()) < 300
