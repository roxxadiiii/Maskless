"""Evidence checks for graph relabelling invariance."""

from dataclasses import dataclass

import networkx as nx

from src.errors import InvariantError
from src.metrics import unique_stats
from src.signature import signatures


@dataclass(frozen=True)
class RelabelVerification:
    """Relabelling evidence required to confirm structure was preserved."""

    named_unique_count: int
    anonymized_unique_count: int
    named_unique_fraction: float
    anonymized_unique_fraction: float
    count_matches: bool
    signature_multiset_matches: bool
    per_node_signatures_match: bool
    mapped_edges_match: bool
    isomorphic: bool

    @property
    def passed(self) -> bool:
        """Return whether every structural invariance check passed."""
        return all(
            (
                self.count_matches,
                self.signature_multiset_matches,
                self.per_node_signatures_match,
                self.mapped_edges_match,
                self.isomorphic,
            )
        )


def verify_relabel(
    named: nx.Graph,
    anonymized: nx.Graph,
    mapping: dict[str, str],
) -> RelabelVerification:
    """Compare signatures and edges before and after the bijective relabelling."""
    if set(mapping) != set(named) or set(mapping.values()) != set(anonymized):
        raise InvariantError("Relabelling mapping does not cover both graphs.")

    named_signatures = signatures(named)
    anonymized_signatures = signatures(anonymized)
    named_unique = unique_stats(named_signatures)
    anonymized_unique = unique_stats(anonymized_signatures)
    signature_multiset_matches = sorted(named_signatures.values()) == sorted(
        anonymized_signatures.values()
    )
    per_node_signatures_match = all(
        named_signatures[name] == anonymized_signatures[mapping[name]]
        for name in named
    )
    mapped_edges = {
        frozenset((mapping[left], mapping[right]))
        for left, right in named.edges()
    }
    anonymized_edges = {frozenset(edge) for edge in anonymized.edges()}
    mapped_edges_match = mapped_edges == anonymized_edges

    return RelabelVerification(
        named_unique_count=named_unique.unique_count,
        anonymized_unique_count=anonymized_unique.unique_count,
        named_unique_fraction=named_unique.unique_fraction,
        anonymized_unique_fraction=anonymized_unique.unique_fraction,
        count_matches=named_unique.unique_count == anonymized_unique.unique_count,
        signature_multiset_matches=signature_multiset_matches,
        per_node_signatures_match=per_node_signatures_match,
        mapped_edges_match=mapped_edges_match,
        isomorphic=nx.is_isomorphic(named, anonymized),
    )
