import random

import networkx as nx
import pytest

from src.config import Config
from src.generate import InvariantError, baseline_stats, make_named_graph, validate_graph
from src.names import build_names


def test_generation_is_deterministic_and_satisfies_graph_invariants():
    config = Config()
    first = make_named_graph(config)
    second = make_named_graph(config)
    assert type(first) is nx.Graph
    assert set(first) == set(second)
    assert {frozenset(edge) for edge in first.edges()} == {
        frozenset(edge) for edge in second.edges()
    }
    assert len(first) == 100
    assert nx.number_of_selfloops(first) == 0
    assert not list(nx.isolates(first))
    assert all(isinstance(node, str) for node in first)
    assert all(not attrs for _, attrs in first.nodes(data=True))


def test_generator_can_be_selected_by_name():
    graph = make_named_graph(Config(n=20, m_attach=2, model="barabasi_albert"))
    assert len(graph) == 20
    assert not list(nx.isolates(graph))


def test_baseline_stats_describe_the_graph():
    graph = make_named_graph(Config(n=20))
    stats = baseline_stats(graph)
    assert stats["n"] == 20
    assert stats["m"] == graph.number_of_edges()
    assert stats["total_triangles"] == sum(nx.triangles(graph).values()) // 3
    assert sum(stats["degree_histogram"].values()) == 20


def test_name_pool_is_unique_and_bounded():
    names = build_names(100, random.Random(43))
    assert len(names) == len(set(names)) == 100
    with pytest.raises(ValueError, match="at most 100"):
        build_names(101, random.Random(43))


def test_graph_validation_rejects_isolates():
    graph = nx.Graph()
    graph.add_nodes_from(["A", "B"])
    with pytest.raises(InvariantError, match="isolated"):
        validate_graph(graph, 2)
