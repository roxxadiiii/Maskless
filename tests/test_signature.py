import networkx as nx

from src.signature import signatures


def test_signature_uses_degree_and_per_node_triangle_count():
    graph = nx.cycle_graph(4)
    signature = signatures(graph)
    assert set(signature.values()) == {(2, 0)}
    assert all(type(value) is tuple for value in signature.values())
    assert all(type(part) is int for value in signature.values() for part in value)


def test_triangle_counts_are_per_node():
    graph = nx.complete_graph(3)
    assert set(signatures(graph).values()) == {(2, 1)}
