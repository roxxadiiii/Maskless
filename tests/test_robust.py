import networkx as nx
import pytest

from src.robust import _percentile, run_robustness


def test_percentile_uses_linear_interpolation():
    assert _percentile([0.0, 10.0], 5) == pytest.approx(0.5)
    assert _percentile([0.0, 10.0], 95) == pytest.approx(9.5)


def test_robustness_summarizes_seeded_runs_on_fixed_graph():
    graph = nx.relabel_nodes(
        nx.powerlaw_cluster_graph(30, 2, 0.5, seed=12),
        {node: f"U{node:03d}" for node in range(30)},
    )
    original_edges = set(graph.edges())

    result = run_robustness(graph, 0.1, 10, 5, 1042)
    repeated = run_robustness(graph, 0.1, 10, 5, 1042)

    assert result == repeated
    assert result["runs"] == 10
    assert result["seed_start"] == 1042
    assert result["seed_end"] == 1051
    assert [sample["seed"] for sample in result["samples"]] == list(range(1042, 1052))
    assert set(graph.edges()) == original_edges
    assert set(result["summaries"]) == {
        "unique_fraction_after",
        "average_clustering_after",
        "top_k_overlap",
    }
    for summary in result["summaries"].values():
        assert summary["minimum"] <= summary["mean"] <= summary["maximum"]
        assert summary["minimum"] <= summary["percentile_05"]
        assert summary["percentile_05"] <= summary["percentile_95"]
        assert summary["percentile_95"] <= summary["maximum"]


def test_robustness_rejects_zero_runs():
    with pytest.raises(ValueError, match="at least 1"):
        run_robustness(nx.path_graph(["U001", "U002", "U003"]), 0.1, 0, 2, 1)
