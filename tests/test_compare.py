import random

import networkx as nx
import pytest

from src.compare import compare_graphs, comparison_table_rows
from src.perturb import perturb_graph
from src.signature import signatures
from src.metrics import unique_stats


def _named_graph(graph):
    return nx.relabel_nodes(graph, {node: f"U{node + 1:03d}" for node in graph})


def test_zero_perturbation_is_an_identity_for_comparison_metrics():
    graph = _named_graph(nx.powerlaw_cluster_graph(30, 2, 0.5, seed=12))
    identity = perturb_graph(graph, 0, random.Random(2))
    result = compare_graphs(graph, identity.graph, 5)
    assert result["unique"]["count_change"] == 0
    assert result["unique"]["fraction_change"] == 0
    assert result["clustering"]["absolute_change"] == 0
    assert result["ranking"]["same_order"]
    assert result["ranking"]["overlap_count"] == 5


def test_clustering_uses_average_local_coefficient():
    before = _named_graph(nx.cycle_graph(8))
    after = before.copy()
    after.add_edge("U001", "U003")
    result = compare_graphs(before, after, 3)
    assert result["clustering"]["before"] == pytest.approx(
        nx.average_clustering(before, count_zeros=True)
    )
    assert result["clustering"]["after"] == pytest.approx(
        sum(nx.clustering(after).values()) / len(after)
    )


def test_rank_five_tie_is_reported():
    graph = _named_graph(nx.star_graph(5))
    result = compare_graphs(graph, graph.copy(), 5)
    assert result["ranking"]["tie_at_k_before"]
    assert result["ranking"]["tie_at_k_after"]


def test_unique_signature_persistence_matches_hand_calculation():
    before = _named_graph(nx.star_graph(3))
    after = before.copy()
    after.add_edge("U002", "U003")
    result = compare_graphs(before, after, 2)
    assert result["unique"]["originally_unique_count"] == 1
    assert result["unique"]["unchanged_signature_count"] == 0
    assert result["unique"]["unchanged_signature_fraction"] == 0
    assert result["unique"]["still_unique_count"] == 1
    assert result["unique"]["still_unique_fraction"] == 1


def test_persistence_is_not_applicable_when_no_nodes_are_unique():
    graph = _named_graph(nx.cycle_graph(8))
    result = compare_graphs(graph, graph.copy(), 3)
    assert result["unique"]["originally_unique_count"] == 0
    assert result["unique"]["unchanged_signature_fraction"] is None
    assert result["unique"]["still_unique_fraction"] is None
    assert result["clustering"]["relative_change"] is None


def test_top_k_is_deterministic_and_comparison_table_is_complete():
    graph = _named_graph(nx.star_graph(5))
    first = compare_graphs(graph, graph.copy(), 5)
    second = compare_graphs(graph, graph.copy(), 5)
    assert first["ranking"]["before"] == second["ranking"]["before"]
    metrics = {row[0] for row in comparison_table_rows(first)}
    assert {
        "Unique node count",
        "Unique fraction (change in percentage points)",
        "Average clustering",
        "Top-k degree ranking",
    }.issubset(metrics)


def test_uniqueness_count_is_an_integer_metric():
    graph = _named_graph(nx.path_graph(4))
    assert isinstance(unique_stats(signatures(graph)).unique_count, int)
