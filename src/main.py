"""Command-line orchestration for the synthetic network study."""

import csv
from dataclasses import asdict, dataclass
import json
import logging
import platform
import random
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Optional

import networkx as nx

from src.anonymize import anonymize_graph
from src.compare import compare_graphs
from src.config import Config, parse_config
from src.errors import InvariantError
from src.generate import baseline_stats, make_named_graph
from src.metrics import UniquenessStats, unique_stats
from src.perturb import PerturbationResult, perturb_graph
from src.report import (
    write_comparison_figures,
    write_comparison_outputs,
    write_robustness_markdown,
)
from src.robust import run_robustness
from src.signature import signatures
from src.verify import RelabelVerification, verify_relabel


@dataclass(frozen=True)
class PipelineResult:
    """All in-memory products needed to write one experiment's outputs."""

    named_graph: nx.Graph
    baseline: dict[str, Any]
    named_uniqueness: UniquenessStats
    anonymized_graph: nx.Graph
    mapping: dict[str, str]
    verification: RelabelVerification
    anonymized_uniqueness: UniquenessStats
    perturbation: PerturbationResult
    comparison: dict[str, Any]
    robustness: dict[str, Any]


def _configure_logging(config: Config, timestamp: str) -> None:
    """Write environment metadata and initialize the run log."""
    config.out_dir.mkdir(parents=True, exist_ok=True)
    logging.basicConfig(
        filename=config.out_dir / "run.log",
        filemode="w",
        level=logging.INFO,
        format="%(asctime)s %(levelname)s %(message)s",
        force=True,
    )
    environment = {
        "python": platform.python_version(),
        "networkx": nx.__version__,
        "timestamp": timestamp,
        "config": {
            "n": config.n,
            "model": config.model,
            "m_attach": config.m_attach,
            "p_triad": config.p_triad,
            "master_seed": config.master_seed,
            "rewire_fraction": config.rewire_fraction,
            "top_k": config.top_k,
            "robust_runs": config.robust_runs,
            "out_dir": str(config.out_dir),
            "no_plots": config.no_plots,
        },
        "seeds": config.seeds,
    }
    _write_json(config.out_dir / "environment.txt", environment)
    logging.info("Run started: %s", json.dumps(environment, sort_keys=True))


def _write_json(path: Path, payload: Any) -> None:
    """Write indented, key-sorted JSON using UTF-8."""
    path.write_text(
        json.dumps(payload, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )


def _run_generation(config: Config) -> tuple[nx.Graph, dict[str, Any], UniquenessStats]:
    logging.info("Starting P1 synthetic network generation.")
    graph = make_named_graph(config)
    baseline = baseline_stats(graph)
    logging.info("Finished P1 synthetic network generation.")

    logging.info("Starting P2 signature computation.")
    uniqueness = unique_stats(signatures(graph))
    logging.info("Finished P2/P3 signature and uniqueness analysis.")
    return graph, baseline, uniqueness


def _run_anonymization(
    config: Config, named_graph: nx.Graph
) -> tuple[nx.Graph, dict[str, str], RelabelVerification, UniquenessStats]:
    logging.info("Starting P4 anonymisation.")
    anonymized, mapping = anonymize_graph(
        named_graph, random.Random(config.seeds["anon"])
    )
    logging.info("Finished P4 anonymisation.")

    logging.info("Starting P5 relabelling verification.")
    verification = verify_relabel(named_graph, anonymized, mapping)
    if not verification.passed:
        raise InvariantError("Relabelling invariance verification failed.")
    anonymized_uniqueness = unique_stats(signatures(anonymized))
    logging.info("Finished P5 relabelling verification.")
    logging.info(
        "Relabelling preserved structure: before=%d/%d after=%d/%d changed=%s",
        verification.named_unique_count,
        len(named_graph),
        verification.anonymized_unique_count,
        len(anonymized),
        not verification.count_matches,
    )
    logging.info(
        "Relabelling changes labels, not graph structure or structural signatures."
    )
    return anonymized, mapping, verification, anonymized_uniqueness


def _run_perturbation_and_comparison(
    config: Config, anonymized: nx.Graph
) -> tuple[PerturbationResult, dict[str, Any]]:
    logging.info("Starting P6 edge perturbation.")
    perturbation = perturb_graph(
        anonymized,
        config.rewire_fraction,
        random.Random(config.seeds["perturb"]),
    )
    logging.info("Finished P6 edge perturbation.")
    logging.info(
        "Edge replacement: m=%d k=%d fraction=%s (round half up).",
        perturbation.edge_count,
        perturbation.replacement_count,
        config.rewire_fraction,
    )

    logging.info("Starting P7 graph comparison.")
    comparison = compare_graphs(anonymized, perturbation.graph, config.top_k)
    logging.info("Finished P7 graph comparison.")
    return perturbation, comparison


def _execute_pipeline(config: Config) -> PipelineResult:
    named_graph, baseline, named_uniqueness = _run_generation(config)
    anonymized, mapping, verification, anonymized_uniqueness = _run_anonymization(
        config, named_graph
    )
    perturbation, comparison = _run_perturbation_and_comparison(config, anonymized)
    logging.info(
        "Starting P8.1 robustness analysis with %d perturbation seeds.",
        config.robust_runs,
    )
    robustness = run_robustness(
        anonymized,
        config.rewire_fraction,
        config.robust_runs,
        config.top_k,
        config.seeds["robust_base"],
    )
    logging.info(
        "Robustness summaries: %s",
        json.dumps(robustness["summaries"], sort_keys=True),
    )
    logging.info("Finished P8.1 robustness analysis.")
    return PipelineResult(
        named_graph=named_graph,
        baseline=baseline,
        named_uniqueness=named_uniqueness,
        anonymized_graph=anonymized,
        mapping=mapping,
        verification=verification,
        anonymized_uniqueness=anonymized_uniqueness,
        perturbation=perturbation,
        comparison=comparison,
        robustness=robustness,
    )


def _shuffled_edges(graph: nx.Graph, seed: int) -> list[tuple[str, str]]:
    edges = [tuple(sorted(edge)) for edge in graph.edges()]
    random.Random(seed).shuffle(edges)
    return edges


def _write_edge_csv(path: Path, edges: list[tuple[str, str]]) -> None:
    with path.open("w", encoding="utf-8", newline="") as stream:
        writer = csv.writer(stream)
        writer.writerow(("u", "v"))
        writer.writerows(edges)


def _write_private_outputs(config: Config, result: PipelineResult) -> None:
    private_dir = Path("private")
    private_dir.mkdir(parents=True, exist_ok=True)
    _write_edge_csv(
        private_dir / "G_named_edges.csv",
        _shuffled_edges(result.named_graph, config.seeds["names"]),
    )
    _write_json(private_dir / "mapping_private.json", result.mapping)


def _uniqueness_output(result: PipelineResult) -> dict[str, Any]:
    named = result.named_uniqueness
    anonymized = result.anonymized_uniqueness
    return {
        "named": {
            "unique_signatures": named.unique_signatures,
            "unique_count": named.unique_count,
            "unique_fraction": named.unique_fraction,
            "distinct_signatures": named.distinct_signatures,
            "largest_class_size": named.largest_class_size,
            "class_size_histogram": named.class_size_histogram,
        },
        "anonymized": {
            "unique_count": anonymized.unique_count,
            "unique_fraction": anonymized.unique_fraction,
        },
    }


def _verification_output(verification: RelabelVerification) -> dict[str, Any]:
    return asdict(verification) | {"passed": verification.passed}


def _comparison_results(comparison: dict[str, Any]) -> dict[str, Any]:
    unique = comparison["unique"]
    ranking = comparison["ranking"]
    top_k = comparison["top_k"]
    return {
        "top_k": top_k,
        "top_k_before": ranking["before"],
        "top_k_after": ranking["after"],
        "top_k_overlap": ranking["overlap_count"],
        "top_k_same_order": ranking["same_order"],
        "top_k_tie": {
            "before": ranking["tie_at_k_before"],
            "after": ranking["tie_at_k_after"],
        },
        "unique_before": {
            "count": unique["before"]["count"],
            "fraction": unique["before"]["fraction"],
        },
        "unique_after": {
            "count": unique["after"]["count"],
            "fraction": unique["after"]["fraction"],
        },
        "clustering_before": comparison["clustering"]["before"],
        "clustering_after": comparison["clustering"]["after"],
        "top5_before": ranking["before"] if top_k == 5 else None,
        "top5_after": ranking["after"] if top_k == 5 else None,
        "top5_overlap": ranking["overlap_count"] if top_k == 5 else None,
        "top5_same_order": ranking["same_order"] if top_k == 5 else None,
        "top5_tie_at_5": (
            ranking["tie_at_k_before"] or ranking["tie_at_k_after"]
            if top_k == 5
            else None
        ),
        "top5_tie_at_5_before": ranking["tie_at_k_before"] if top_k == 5 else None,
        "top5_tie_at_5_after": ranking["tie_at_k_after"] if top_k == 5 else None,
        "unique_persist_signature": unique["unchanged_signature_fraction"],
        "unique_persist_unique": unique["still_unique_fraction"],
        "details": comparison,
    }


def _results_payload(
    config: Config, result: PipelineResult, timestamp: str
) -> dict[str, Any]:
    verification = result.verification
    return {
        "meta": {
            "python": platform.python_version(),
            "networkx": nx.__version__,
            "timestamp": timestamp,
            "seeds": {
                name: config.seeds[name]
                for name in ("master", "names", "anon", "perturb")
            },
        },
        "config": {
            "n": config.n,
            "model": config.model,
            "m_attach": config.m_attach,
            "p_triad": config.p_triad,
            "master_seed": config.master_seed,
            "rewire_fraction": config.rewire_fraction,
            "top_k": config.top_k,
            "robust_runs": config.robust_runs,
            "out_dir": str(config.out_dir),
            "no_plots": config.no_plots,
        },
        "baseline": result.baseline,
        "named": {
            "unique_count": result.named_uniqueness.unique_count,
            "unique_fraction": result.named_uniqueness.unique_fraction,
        },
        "anon": {
            "unique_count": result.anonymized_uniqueness.unique_count,
            "unique_fraction": result.anonymized_uniqueness.unique_fraction,
        },
        "relabel": {
            "fraction_changed": not verification.count_matches,
            "per_node_match": verification.per_node_signatures_match,
            "edges_match": verification.mapped_edges_match,
            "isomorphic": verification.isomorphic,
        },
        "perturb": {
            "m": result.perturbation.edge_count,
            "k": result.perturbation.replacement_count,
            "removed": result.perturbation.removed_edges,
            "added": result.perturbation.added_edges,
        },
        "compare": _comparison_results(result.comparison),
        "robust": result.robustness,
    }


def _write_shareable_outputs(
    config: Config, result: PipelineResult, timestamp: str
) -> str:
    _write_edge_csv(
        config.out_dir / "G_anon_edges.csv",
        _shuffled_edges(result.anonymized_graph, config.seeds["anon"]),
    )
    _write_json(config.out_dir / "baseline.json", result.baseline)
    _write_json(config.out_dir / "uniqueness.json", _uniqueness_output(result))
    _write_json(
        config.out_dir / "relabel_verification.json",
        _verification_output(result.verification),
    )
    _write_json(
        config.out_dir / "perturbation.json",
        {
            "edge_count": result.perturbation.edge_count,
            "replacement_count": result.perturbation.replacement_count,
            "fraction": config.rewire_fraction,
            "rounding": "round half up: int(fraction * m + 0.5)",
            "removed_edges": result.perturbation.removed_edges,
            "added_edges": result.perturbation.added_edges,
        },
    )
    _write_json(config.out_dir / "robust.json", result.robustness)
    _write_json(
        config.out_dir / "results.json",
        _results_payload(config, result, timestamp),
    )
    write_robustness_markdown(config.out_dir, result.robustness)
    table = write_comparison_outputs(config.out_dir, result.comparison)
    if not config.no_plots:
        write_comparison_figures(
            config.out_dir,
            result.anonymized_graph,
            result.perturbation.graph,
            result.comparison,
        )
    return table


def _print_summary(config: Config, result: PipelineResult, table: str) -> None:
    verification = result.verification
    print(
        "Unique fraction before = "
        f"{verification.named_unique_fraction:.4f} "
        f"({verification.named_unique_count}/{config.n}), after = "
        f"{verification.anonymized_unique_fraction:.4f} "
        f"({verification.anonymized_unique_count}/{config.n}), changed = "
        f"{not verification.count_matches}"
    )
    print(table, end="")


def run(config: Config) -> int:
    """Run phases P1-P8.1, persist safe outputs and print their summary."""
    timestamp = datetime.now(timezone.utc).isoformat()
    _configure_logging(config, timestamp)
    try:
        result = _execute_pipeline(config)
    except InvariantError as error:
        logging.exception("Internal graph invariant failed.")
        print(f"error: internal graph invariant failed: {error}", file=sys.stderr)
        return 2
    except ValueError as error:
        logging.error("Run failed: %s", error)
        print(f"error: {error}", file=sys.stderr)
        return 1

    table = _write_shareable_outputs(config, result, timestamp)
    _write_private_outputs(config, result)
    logging.info("Baseline statistics: %s", json.dumps(result.baseline, sort_keys=True))
    _print_summary(config, result, table)
    return 0


def main(argv: Optional[list[str]] = None) -> int:
    """Parse, validate and execute the project workflow."""
    try:
        config = parse_config(argv)
    except ValueError as error:
        print(f"error: {error}", file=sys.stderr)
        return 1
    return run(config)


if __name__ == "__main__":
    raise SystemExit(main())
