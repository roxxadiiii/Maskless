"""Command-line entry point for the current setup and generation workflow."""

import json
import csv
import logging
import platform
import random
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

import networkx as nx

from src.config import Config, parse_config
from src.anonymize import anonymize_graph
from src.errors import InvariantError
from src.generate import baseline_stats, make_named_graph
from src.metrics import unique_stats
from src.signature import signatures
from src.verify import verify_relabel


def _configure_logging(config: Config, timestamp: str) -> None:
    """Initialize a fresh run log with environment and reproducibility details."""
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
    (config.out_dir / "environment.txt").write_text(
        json.dumps(environment, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    logging.info("Run started: %s", json.dumps(environment, sort_keys=True))


def run(config: Config) -> int:
    """Generate the baseline network and save its private edge list and stats."""
    timestamp = datetime.now(timezone.utc).isoformat()
    _configure_logging(config, timestamp)
    logging.info("Starting P1 synthetic network generation.")
    try:
        graph = make_named_graph(config)
        stats = baseline_stats(graph)
        named_signatures = signatures(graph)
        named_uniqueness = unique_stats(named_signatures)
        anonymized, mapping = anonymize_graph(
            graph, random.Random(config.seeds["anon"])
        )
        verification = verify_relabel(graph, anonymized, mapping)
        if not verification.passed:
            raise InvariantError("Relabelling invariance verification failed.")
        anonymized_uniqueness = unique_stats(signatures(anonymized))
        logging.info(
            "Relabelling preserved structure: before=%d/%d after=%d/%d changed=%s",
            verification.named_unique_count,
            config.n,
            verification.anonymized_unique_count,
            config.n,
            not verification.count_matches,
        )
        logging.info(
            "Relabelling changes labels, not graph structure or structural signatures."
        )
    except InvariantError as error:
        logging.exception("Internal graph invariant failed.")
        print(f"error: internal graph invariant failed: {error}", file=sys.stderr)
        return 2
    except ValueError as error:
        logging.error("Generation failed: %s", error)
        print(f"error: {error}", file=sys.stderr)
        return 1

    private_dir = Path("private")
    private_dir.mkdir(parents=True, exist_ok=True)
    edge_rows = [tuple(sorted(edge)) for edge in graph.edges()]
    random.Random(config.seeds["names"]).shuffle(edge_rows)
    with (private_dir / "G_named_edges.csv").open(
        "w", encoding="utf-8", newline=""
    ) as stream:
        writer = csv.writer(stream)
        writer.writerow(("u", "v"))
        writer.writerows(edge_rows)
    (private_dir / "mapping_private.json").write_text(
        json.dumps(mapping, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    anonymized_rows = [tuple(sorted(edge)) for edge in anonymized.edges()]
    random.Random(config.seeds["anon"]).shuffle(anonymized_rows)
    with (config.out_dir / "G_anon_edges.csv").open(
        "w", encoding="utf-8", newline=""
    ) as stream:
        writer = csv.writer(stream)
        writer.writerow(("u", "v"))
        writer.writerows(anonymized_rows)

    (config.out_dir / "baseline.json").write_text(
        json.dumps(stats, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    uniqueness_summary = {
        "named": {
            "unique_signatures": named_uniqueness.unique_signatures,
            "unique_count": named_uniqueness.unique_count,
            "unique_fraction": named_uniqueness.unique_fraction,
            "distinct_signatures": named_uniqueness.distinct_signatures,
            "largest_class_size": named_uniqueness.largest_class_size,
            "class_size_histogram": named_uniqueness.class_size_histogram,
        },
        "anonymized": {
            "unique_count": anonymized_uniqueness.unique_count,
            "unique_fraction": anonymized_uniqueness.unique_fraction,
        },
    }
    verification_summary = {
        "named_unique_count": verification.named_unique_count,
        "anonymized_unique_count": verification.anonymized_unique_count,
        "named_unique_fraction": verification.named_unique_fraction,
        "anonymized_unique_fraction": verification.anonymized_unique_fraction,
        "count_matches": verification.count_matches,
        "signature_multiset_matches": verification.signature_multiset_matches,
        "per_node_signatures_match": verification.per_node_signatures_match,
        "mapped_edges_match": verification.mapped_edges_match,
        "isomorphic": verification.isomorphic,
        "passed": verification.passed,
    }
    (config.out_dir / "uniqueness.json").write_text(
        json.dumps(uniqueness_summary, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    (config.out_dir / "relabel_verification.json").write_text(
        json.dumps(verification_summary, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    logging.info("Finished P1 generation: %s", json.dumps(stats, sort_keys=True))
    logging.info(
        "Finished P2-P5 signature, uniqueness and relabelling verification."
    )
    print(json.dumps(stats, indent=2, sort_keys=True))
    print(json.dumps(uniqueness_summary, indent=2, sort_keys=True))
    print(
        "Unique fraction before = "
        f"{verification.named_unique_fraction:.4f} "
        f"({verification.named_unique_count}/{config.n}), after = "
        f"{verification.anonymized_unique_fraction:.4f} "
        f"({verification.anonymized_unique_count}/{config.n}), changed = "
        f"{not verification.count_matches}"
    )
    return 0


def main(argv: Optional[list[str]] = None) -> int:
    """Parse, validate and execute the current project workflow."""
    try:
        config = parse_config(argv)
    except ValueError as error:
        print(f"error: {error}", file=sys.stderr)
        return 1
    return run(config)


if __name__ == "__main__":
    raise SystemExit(main())
