import networkx as nx

from src.anonymize import anonymize_graph
from src.verify import verify_relabel
import random


def test_relabel_verification_confirms_exact_invariance():
    named = nx.powerlaw_cluster_graph(20, 2, 0.4, seed=4)
    named = nx.relabel_nodes(named, {node: f"Name {node}" for node in named})
    anonymized, mapping = anonymize_graph(named, random.Random(9))
    result = verify_relabel(named, anonymized, mapping)
    assert result.passed
    assert result.count_matches
    assert result.signature_multiset_matches
    assert result.per_node_signatures_match
    assert result.mapped_edges_match
    assert result.isomorphic
    assert result.named_unique_count == result.anonymized_unique_count


def test_negative_control_detects_an_edge_change():
    named = nx.cycle_graph(["Name A", "Name B", "Name C", "Name D"])
    anonymized, mapping = anonymize_graph(named, random.Random(3))
    anonymized.remove_edge(*next(iter(anonymized.edges())))
    result = verify_relabel(named, anonymized, mapping)
    assert not result.passed
    assert not result.count_matches or not result.signature_multiset_matches
