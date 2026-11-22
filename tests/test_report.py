import csv
import json

import networkx as nx
import pytest

from src.compare import compare_graphs
from src.report import (
    write_comparison_figures,
    write_comparison_outputs,
    write_robustness_markdown,
)


def test_comparison_outputs_are_written_and_parseable(tmp_path):
    graph = nx.star_graph(5)
    graph = nx.relabel_nodes(graph, {node: f"U{node + 1:03d}" for node in graph})
    comparison = compare_graphs(graph, graph.copy(), 5)

    markdown = write_comparison_outputs(tmp_path, comparison)

    assert (tmp_path / "comparison.json").is_file()
    assert (tmp_path / "comparison.md").read_text() == markdown
    with (tmp_path / "comparison.csv").open(newline="") as stream:
        rows = list(csv.reader(stream))
    assert rows[0] == ["Metric", "Before", "After", "Change"]
    assert {row[0] for row in rows[1:]} == {
        "Unique node count",
        "Unique fraction (change in percentage points)",
        "Distinct signatures",
        "Largest signature class",
        "Average clustering",
        "Clustering relative change (%)",
        "Top-k degree ranking",
        "Transitivity",
        "Connected components",
    }
    parsed = json.loads((tmp_path / "comparison.json").read_text())
    assert parsed["ranking"]["before"][0] == ["U001", 5]


def test_comparison_figures_are_written_when_matplotlib_is_available(tmp_path):
    pytest.importorskip("matplotlib")
    graph = nx.star_graph(5)
    graph = nx.relabel_nodes(graph, {node: f"U{node + 1:03d}" for node in graph})
    comparison = compare_graphs(graph, graph.copy(), 5)

    assert write_comparison_figures(tmp_path, graph, graph.copy(), comparison)
    assert {
        path.name for path in (tmp_path / "figures").glob("*.png")
    } == {
        "class_size_histogram.png",
        "degree_vs_triangles.png",
        "top_k_degrees.png",
    }


def test_robustness_markdown_reports_spread_and_fixed_base_caveat(tmp_path):
    robustness = {
        "runs": 2,
        "top_k": 5,
        "summaries": {
            "unique_fraction_after": {
                "mean": 0.4,
                "standard_deviation": 0.1,
                "minimum": 0.3,
                "percentile_05": 0.31,
                "percentile_95": 0.49,
                "maximum": 0.5,
            },
            "average_clustering_after": {
                "mean": 0.2,
                "standard_deviation": 0.0,
                "minimum": 0.2,
                "percentile_05": 0.2,
                "percentile_95": 0.2,
                "maximum": 0.2,
            },
            "top_k_overlap": {
                "mean": 4.0,
                "standard_deviation": 0.0,
                "minimum": 4.0,
                "percentile_05": 4.0,
                "percentile_95": 4.0,
                "maximum": 4.0,
            },
        },
    }

    markdown = write_robustness_markdown(tmp_path, robustness)

    assert (tmp_path / "robust.md").read_text(encoding="utf-8") == markdown
    assert "Unique fraction after" in markdown
    assert "varied from 0.3000 to 0.5000" in markdown
    assert "was constant from 0.2000 to 0.2000" in markdown
    assert "fixed graph and seed sequence only" in markdown
