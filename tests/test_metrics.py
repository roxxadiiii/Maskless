import networkx as nx
import pytest

from src.metrics import unique_stats
from src.signature import signatures


def test_path_of_four_has_no_unique_signatures():
    stats = unique_stats(signatures(nx.path_graph(4)))
    assert stats.unique_count == 0
    assert stats.unique_fraction == 0
    assert stats.class_size_histogram == {2: 2}


def test_five_leaf_star_has_one_unique_hub():
    stats = unique_stats(signatures(nx.star_graph(5)))
    assert stats.unique_count == 1
    assert stats.unique_fraction == pytest.approx(1 / 6)
    assert stats.class_size_histogram == {1: 1, 5: 1}


def test_regular_cycle_has_no_unique_signatures():
    stats = unique_stats(signatures(nx.cycle_graph(10)))
    assert stats.unique_count == 0
    assert stats.largest_class_size == 10


def test_empty_signature_input_is_rejected():
    with pytest.raises(ValueError, match="empty graph"):
        unique_stats({})
