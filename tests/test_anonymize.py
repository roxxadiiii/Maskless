import random
import re

import networkx as nx
import pytest

from src.anonymize import anonymize_graph, check_leakage, make_mapping
from src.errors import InvariantError


def test_mapping_is_a_seeded_bijection_with_valid_ids():
    graph = nx.path_graph(["A Name", "B Name", "C Name"])
    first = make_mapping(graph, random.Random(12))
    second = make_mapping(graph, random.Random(12))
    assert first == second
    assert set(first) == set(graph)
    assert len(set(first.values())) == graph.number_of_nodes()
    assert all(re.fullmatch(r"U\d{3,}", user_id) for user_id in first.values())


def test_anonymize_copies_graph_and_leaves_no_names_or_attributes():
    graph = nx.path_graph(["A Name", "B Name", "C Name"])
    original_edges = {frozenset(edge) for edge in graph.edges()}
    anonymized, mapping = anonymize_graph(graph, random.Random(7))
    assert set(graph) == set(mapping)
    assert set(anonymized) == set(mapping.values())
    assert set(graph.nodes()) == {"A Name", "B Name", "C Name"}
    assert original_edges == {frozenset(edge) for edge in graph.edges()}
    assert not (set(graph) & set(anonymized))
    assert all(not data for _, data in anonymized.nodes(data=True))
    assert not anonymized.graph


def test_leakage_check_finds_names_in_nested_attributes():
    graph = nx.Graph()
    graph.add_edge("U001", "U002", note={"source": ["A Name"]})
    with pytest.raises(InvariantError, match="attributes"):
        check_leakage(graph, {"A Name"})
