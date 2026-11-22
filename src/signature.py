"""Structural signatures based on node degree and triangle count."""

from typing import Hashable

import networkx as nx

from src.errors import InvariantError


def signatures(graph: nx.Graph) -> dict[Hashable, tuple[int, int]]:
    """Compute each node's (degree, triangles) signature and verify identities."""
    degrees = dict(graph.degree())
    triangles = nx.triangles(graph)
    if sum(degrees.values()) != 2 * graph.number_of_edges():
        raise InvariantError("Degree sum does not equal twice the edge count.")
    if sum(triangles.values()) % 3:
        raise InvariantError("Triangle counts do not sum to a multiple of three.")

    result: dict[Hashable, tuple[int, int]] = {}
    for node in graph:
        degree = degrees[node]
        triangle_count = triangles[node]
        if not 0 <= triangle_count <= degree * (degree - 1) // 2:
            raise InvariantError("A node has an invalid triangle count.")
        if not isinstance(degree, int) or not isinstance(triangle_count, int):
            raise InvariantError("Degree and triangle counts must be integers.")
        result[node] = (degree, triangle_count)
    return result
