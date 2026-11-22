"""Synthetic graph generation, validation and baseline statistics."""

from collections import Counter
import random
from typing import Any

import networkx as nx

from src.config import Config
from src.errors import InvariantError
from src.names import build_names


def make_named_graph(config: Config) -> nx.Graph:
    """Generate the configured graph with fictional names as its node labels."""
    config.validate()
    names = build_names(config.n, random.Random(config.seeds["names"]))
    if config.model == "powerlaw_cluster":
        base = nx.powerlaw_cluster_graph(
            config.n,
            config.m_attach,
            config.p_triad,
            seed=config.seeds["master"],
        )
    else:
        base = nx.barabasi_albert_graph(
            config.n,
            config.m_attach,
            seed=config.seeds["master"],
        )
    mapping = dict(zip(sorted(base.nodes()), names))
    graph = nx.relabel_nodes(base, mapping, copy=True)
    validate_graph(graph, config.n)
    return graph


def validate_graph(graph: nx.Graph, expected_nodes: int) -> None:
    """Fail loudly if the graph is not a simple, named, isolate-free graph."""
    if type(graph) is not nx.Graph:
        raise InvariantError("Generated graph must be exactly an undirected nx.Graph.")
    if graph.number_of_nodes() != expected_nodes:
        raise InvariantError(
            f"Expected {expected_nodes} nodes; found {graph.number_of_nodes()}."
        )
    if nx.number_of_selfloops(graph):
        raise InvariantError("Generated graph contains self-loops.")
    if list(nx.isolates(graph)):
        raise InvariantError("Generated graph contains isolated nodes.")
    if not all(isinstance(node, str) for node in graph):
        raise InvariantError("Every node label must be a string.")
    if any(data for _, data in graph.nodes(data=True)):
        raise InvariantError("Node attributes must be empty; names belong in labels only.")
    if any(data for _, _, data in graph.edges(data=True)):
        raise InvariantError("Edge attributes must be empty.")
    if graph.graph:
        raise InvariantError("Graph attributes must be empty.")


def baseline_stats(graph: nx.Graph) -> dict[str, Any]:
    """Compute descriptive baseline statistics from the generated graph."""
    degrees = dict(graph.degree())
    triangles = nx.triangles(graph)
    degree_histogram = dict(sorted(Counter(degrees.values()).items()))
    return {
        "n": graph.number_of_nodes(),
        "m": graph.number_of_edges(),
        "density": nx.density(graph),
        "degree_min": min(degrees.values()),
        "degree_mean": sum(degrees.values()) / len(degrees),
        "degree_max": max(degrees.values()),
        "components": nx.number_connected_components(graph),
        "connected": nx.is_connected(graph),
        "total_triangles": sum(triangles.values()) // 3,
        "transitivity": nx.transitivity(graph),
        "avg_clustering": nx.average_clustering(graph, count_zeros=True),
        "degree_histogram": degree_histogram,
    }
