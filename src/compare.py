"""Before/after comparison metrics for the anonymous and perturbed graphs."""

from collections import Counter
from typing import Any, Optional

import networkx as nx

from src.errors import InvariantError
from src.metrics import UniquenessStats, unique_stats
from src.signature import signatures


def _uniqueness_summary(stats: UniquenessStats) -> dict[str, Any]:
    """Summarise unique counts and fractions as exact integers and display floats."""
    return {
        "count": stats.unique_count,
        "fraction": stats.unique_fraction,
        "distinct_signatures": stats.distinct_signatures,
        "largest_class_size": stats.largest_class_size,
        "class_size_histogram": stats.class_size_histogram,
    }


def _ranking(graph: nx.Graph) -> tuple[list[tuple[str, int]], dict[str, int]]:
    """Rank nodes by descending degree with the identifier as a deterministic tie-break."""
    ranked = sorted(graph.degree(), key=lambda item: (-item[1], item[0]))
    return ranked, {node: rank for rank, (node, _) in enumerate(ranked, start=1)}


def _tie_at_k(ranked: list[tuple[str, int]], k: int) -> bool:
    """Report whether degree at rank k is tied with degree at rank k+1."""
    return len(ranked) > k and ranked[k - 1][1] == ranked[k][1]


def _ranking_comparison(
    before: nx.Graph, after: nx.Graph, top_k: int
) -> dict[str, Any]:
    """Compare two rankings by membership, order, and per-node movement."""
    before_ranked, before_ranks = _ranking(before)
    after_ranked, after_ranks = _ranking(after)
    before_top, after_top = before_ranked[:top_k], after_ranked[:top_k]
    top_nodes = sorted({node for node, _ in before_top + after_top})

    def movement(nodes: list[str]) -> list[dict[str, Any]]:
        """Compute per-node rank movement, with positive values meaning improvement."""
        return [
            {
                "id": node,
                "before_rank": before_ranks[node],
                "after_rank": after_ranks[node],
                "movement": before_ranks[node] - after_ranks[node],
            }
            for node in nodes
        ]

    return {
        "before": [[node, degree] for node, degree in before_top],
        "after": [[node, degree] for node, degree in after_top],
        "overlap_count": len(
            {node for node, _ in before_top}.intersection(
                node for node, _ in after_top
            )
        ),
        "same_order": [node for node, _ in before_top]
        == [node for node, _ in after_top],
        "rank_movement": movement(sorted(before_ranks)),
        "top_k_rank_movement": movement(top_nodes),
        "movement_convention": "positive means improved rank",
        "tie_at_k_before": _tie_at_k(before_ranked, top_k),
        "tie_at_k_after": _tie_at_k(after_ranked, top_k),
    }


def _persistence(
    before_signatures: dict[Any, tuple[int, int]],
    after_signatures: dict[Any, tuple[int, int]],
    before_unique: UniquenessStats,
) -> dict[str, Any]:
    """Measure how often originally unique signatures survive perturbation."""
    originally_unique = before_unique.unique_nodes
    after_frequencies = Counter(after_signatures.values())
    unchanged_count = sum(
        before_signatures[node] == after_signatures[node] for node in originally_unique
    )
    still_unique_count = sum(
        after_frequencies[after_signatures[node]] == 1 for node in originally_unique
    )
    denominator = len(originally_unique)
    return {
        "originally_unique_count": denominator,
        "unchanged_signature_count": unchanged_count,
        "unchanged_signature_fraction": unchanged_count / denominator
        if denominator
        else None,
        "still_unique_count": still_unique_count,
        "still_unique_fraction": still_unique_count / denominator
        if denominator
        else None,
        "changed_signature_count": sum(
            before_signatures[node] != after_signatures[node]
            for node in before_signatures
        ),
    }


def _uniqueness_comparison(
    before_signatures: dict[Any, tuple[int, int]],
    after_signatures: dict[Any, tuple[int, int]],
) -> dict[str, Any]:
    """Compare uniqueness in integer counts and percentage points."""
    before_unique = unique_stats(before_signatures)
    after_unique = unique_stats(after_signatures)
    fraction_change = after_unique.unique_fraction - before_unique.unique_fraction
    return {
        "before": _uniqueness_summary(before_unique),
        "after": _uniqueness_summary(after_unique),
        "count_change": after_unique.unique_count - before_unique.unique_count,
        "fraction_change": fraction_change,
        "percentage_point_change": 100 * fraction_change,
        **_persistence(before_signatures, after_signatures, before_unique),
    }


def _clustering_comparison(before: nx.Graph, after: nx.Graph) -> dict[str, Any]:
    """Compare mean local clustering with absolute and relative deltas."""
    before_value = nx.average_clustering(before, count_zeros=True)
    after_value = nx.average_clustering(after, count_zeros=True)
    absolute_change = after_value - before_value
    relative_change: Optional[float] = (
        absolute_change / before_value if before_value != 0 else None
    )
    return {
        "before": before_value,
        "after": after_value,
        "absolute_change": absolute_change,
        "relative_change": relative_change,
        "relative_change_percent": 100 * relative_change
        if relative_change is not None
        else None,
        "definition": "mean of local coefficients, count_zeros=True",
    }


def _degree_change_summary(before: nx.Graph, after: nx.Graph) -> dict[str, Any]:
    """Summarise how node degrees shift after rewiring."""
    changes = [after.degree(node) - before.degree(node) for node in before]
    absolute_changes = [abs(change) for change in changes]
    return {
        "nodes_increased": sum(change > 0 for change in changes),
        "nodes_decreased": sum(change < 0 for change in changes),
        "nodes_unchanged": sum(change == 0 for change in changes),
        "max_absolute_change": max(absolute_changes, default=0),
        "mean_absolute_change": sum(absolute_changes) / len(absolute_changes),
    }


def _supplementary_comparison(
    before: nx.Graph, after: nx.Graph
) -> dict[str, Any]:
    """Collect secondary indicators such as transitivity and components."""
    return {
        "transitivity_before": nx.transitivity(before),
        "transitivity_after": nx.transitivity(after),
        "components_before": nx.number_connected_components(before),
        "components_after": nx.number_connected_components(after),
        "isolates_before": len(list(nx.isolates(before))),
        "isolates_after": len(list(nx.isolates(after))),
        "degree_change_summary": _degree_change_summary(before, after),
    }


def compare_graphs(before: nx.Graph, after: nx.Graph, top_k: int) -> dict[str, Any]:
    """Compare uniqueness, clustering, ranking and supplementary indicators."""
    if set(before) != set(after):
        raise InvariantError("Comparison graphs must have the same node set.")
    if not 1 <= top_k <= before.number_of_nodes():
        raise ValueError("top-k must be at least 1 and no greater than N.")
    if not all(isinstance(node, str) for node in before):
        raise ValueError("Deterministic top-k ranking requires string node labels.")

    before_signatures, after_signatures = signatures(before), signatures(after)
    return {
        "before_graph": "G_anon",
        "after_graph": "G_pert",
        "top_k": top_k,
        "unique": _uniqueness_comparison(
            before_signatures, after_signatures
        ),
        "clustering": _clustering_comparison(before, after),
        "ranking": _ranking_comparison(before, after, top_k),
        "supplementary": _supplementary_comparison(before, after),
    }


def _uniqueness_table_rows(comparison: dict[str, Any]) -> list[tuple[str, Any, Any, Any]]:
    """Format uniqueness rows for the human-readable comparison table."""
    unique = comparison["unique"]
    return [
        (
            "Unique node count",
            unique["before"]["count"],
            unique["after"]["count"],
            unique["count_change"],
        ),
        (
            "Unique fraction (change in percentage points)",
            unique["before"]["fraction"],
            unique["after"]["fraction"],
            unique["percentage_point_change"],
        ),
        (
            "Distinct signatures",
            unique["before"]["distinct_signatures"],
            unique["after"]["distinct_signatures"],
            unique["after"]["distinct_signatures"]
            - unique["before"]["distinct_signatures"],
        ),
        (
            "Largest signature class",
            unique["before"]["largest_class_size"],
            unique["after"]["largest_class_size"],
            unique["after"]["largest_class_size"]
            - unique["before"]["largest_class_size"],
        ),
    ]


def _clustering_table_rows(comparison: dict[str, Any]) -> list[tuple[str, Any, Any, Any]]:
    """Format clustering rows for the human-readable comparison table."""
    clustering = comparison["clustering"]
    return [
        (
            "Average clustering",
            clustering["before"],
            clustering["after"],
            clustering["absolute_change"],
        ),
        (
            "Clustering relative change (%)",
            "N/A",
            "N/A",
            clustering["relative_change_percent"],
        ),
    ]


def _ranking_table_rows(comparison: dict[str, Any]) -> list[tuple[str, Any, Any, Any]]:
    """Format ranking rows for the human-readable comparison table."""
    ranking = comparison["ranking"]
    movement = ", ".join(
        f"{item['id']}:{item['movement']}"
        for item in ranking["top_k_rank_movement"]
    )
    change = (
        f"overlap {ranking['overlap_count']}/{comparison['top_k']}; "
        f"same order={ranking['same_order']}; "
        f"tie at k before/after={ranking['tie_at_k_before']}/"
        f"{ranking['tie_at_k_after']}; movement={movement}"
    )
    return [("Top-k degree ranking", ranking["before"], ranking["after"], change)]


def _supplementary_table_rows(
    comparison: dict[str, Any],
) -> list[tuple[str, Any, Any, Any]]:
    """Format supplementary rows for the human-readable comparison table."""
    supplementary = comparison["supplementary"]
    return [
        (
            "Transitivity",
            supplementary["transitivity_before"],
            supplementary["transitivity_after"],
            supplementary["transitivity_after"]
            - supplementary["transitivity_before"],
        ),
        (
            "Connected components",
            supplementary["components_before"],
            supplementary["components_after"],
            supplementary["components_after"] - supplementary["components_before"],
        ),
    ]


def comparison_table_rows(
    comparison: dict[str, Any],
) -> list[tuple[str, Any, Any, Any]]:
    """Return one consistent Before/After/Change table for required metrics."""
    return (
        _uniqueness_table_rows(comparison)
        + _clustering_table_rows(comparison)
        + _ranking_table_rows(comparison)
        + _supplementary_table_rows(comparison)
    )
