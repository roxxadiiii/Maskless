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


def test_handshake_triangle_identity_and_signature_upper_bound():
    graph = nx.powerlaw_cluster_graph(50, 2, 0.4, seed=8)
    degrees = dict(graph.degree())
    triangles = nx.triangles(graph)

    assert sum(degrees.values()) == 2 * graph.number_of_edges()
    assert sum(triangles.values()) % 3 == 0
    assert all(
        0 <= triangles[node] <= degrees[node] * (degrees[node] - 1) // 2
        for node in graph
    )
