"""Serialization of comparison results and their human-readable table."""

import csv
import json
import logging
from pathlib import Path
from typing import Any

import networkx as nx

from src.compare import comparison_table_rows


def _format_cell(value: Any) -> str:
    if isinstance(value, float):
        return f"{value:.4f}"
    if value is None:
        return "N/A"
    if isinstance(value, (dict, list)):
        return json.dumps(value, sort_keys=True)
    return str(value)


def render_comparison_markdown(comparison: dict[str, Any]) -> str:
    """Render the required Before/After/Change comparison table."""
    lines = [
        "Comparison: anonymized graph before perturbation vs. perturbed graph.",
        "",
        "| Metric | Before | After | Change |",
        "|---|---:|---:|---:|",
    ]
    for row in comparison_table_rows(comparison):
        cells = [_format_cell(cell).replace("|", "\\|") for cell in row]
        lines.append(f"| {cells[0]} | {cells[1]} | {cells[2]} | {cells[3]} |")
    return "\n".join(lines) + "\n"


def write_comparison_outputs(
    output_dir: Path, comparison: dict[str, Any]
) -> str:
    """Write JSON, Markdown and CSV forms of a comparison; return Markdown."""
    output_dir.mkdir(parents=True, exist_ok=True)
    (output_dir / "comparison.json").write_text(
        json.dumps(comparison, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    markdown = render_comparison_markdown(comparison)
    (output_dir / "comparison.md").write_text(markdown, encoding="utf-8")
    with (output_dir / "comparison.csv").open(
        "w", encoding="utf-8", newline=""
    ) as stream:
        writer = csv.writer(stream)
        writer.writerow(("Metric", "Before", "After", "Change"))
        writer.writerows(
            tuple(_format_cell(cell) for cell in row)
            for row in comparison_table_rows(comparison)
        )
    return markdown


def render_robustness_markdown(robustness: dict[str, Any]) -> str:
    """Render observed robustness distributions with fixed-base interpretation."""
    summaries = robustness["summaries"]
    lines = [
        f"Robustness summary for {robustness['runs']} perturbation runs.",
        "",
        "The anonymous base graph is fixed across runs. Standard deviation is "
        "population SD (ddof=0); percentiles use linear interpolation (type 7).",
        "",
        "| Metric | Mean | SD | Min | 5th pct | 95th pct | Max |",
        "|---|---:|---:|---:|---:|---:|---:|",
        *_robustness_table_rows(robustness),
        "",
        _robustness_conclusion(
            robustness,
            summaries["unique_fraction_after"],
            summaries["average_clustering_after"],
            summaries["top_k_overlap"],
        ),
        "",
    ]
    return "\n".join(lines)


def _robustness_table_rows(robustness: dict[str, Any]) -> list[str]:
    labels = (
        ("unique_fraction_after", "Unique fraction after"),
        ("average_clustering_after", "Average clustering after"),
        ("top_k_overlap", f"Top-{robustness['top_k']} overlap (count)"),
    )
    rows = []
    for key, label in labels:
        summary = robustness["summaries"][key]
        cells = (
            label,
            summary["mean"],
            summary["standard_deviation"],
            summary["minimum"],
            summary["percentile_05"],
            summary["percentile_95"],
            summary["maximum"],
        )
        rows.append(
            "| "
            + " | ".join(
                f"{value:.4f}" if isinstance(value, float) else str(value)
                for value in cells
            )
            + " |"
        )
    return rows


def _robustness_conclusion(
    robustness: dict[str, Any],
    uniqueness: dict[str, float],
    clustering: dict[str, float],
    overlap: dict[str, float],
) -> str:
    return (
        f"Across these runs, the unique fraction "
        f"{_spread_word(uniqueness)} from {uniqueness['minimum']:.4f} "
        f"to {uniqueness['maximum']:.4f}, average clustering "
        f"{_spread_word(clustering)} from {clustering['minimum']:.4f} "
        f"to {clustering['maximum']:.4f}, and top-{robustness['top_k']} "
        f"overlap {_spread_word(overlap)} from "
        f"{overlap['minimum']:.4f} to {overlap['maximum']:.4f}. "
        "These ranges describe perturbation-to-perturbation variation for "
        "this fixed graph and seed sequence only; they do not measure "
        "variation between base networks or establish a general result "
        "across graph models."
    )


def write_robustness_markdown(output_dir: Path, robustness: dict[str, Any]) -> str:
    """Write the human-readable robustness summary."""
    output_dir.mkdir(parents=True, exist_ok=True)
    markdown = render_robustness_markdown(robustness)
    (output_dir / "robust.md").write_text(markdown, encoding="utf-8")
    return markdown


def _spread_word(summary: dict[str, float]) -> str:
    """Use neutral wording that reflects whether the observed range varies."""
    return "varied" if summary["minimum"] != summary["maximum"] else "was constant"


def _plot_class_sizes(
    axis: Any, comparison: dict[str, Any], width: float
) -> None:
    before = comparison["unique"]["before"]["class_size_histogram"]
    after = comparison["unique"]["after"]["class_size_histogram"]
    sizes = sorted(set(before) | set(after))
    positions = list(range(len(sizes)))
    axis.bar(
        [position - width / 2 for position in positions],
        [before.get(size, 0) for size in sizes],
        width,
        label="Before",
    )
    axis.bar(
        [position + width / 2 for position in positions],
        [after.get(size, 0) for size in sizes],
        width,
        label="After",
    )
    axis.set_xticks(positions, [str(size) for size in sizes])
    axis.set_xlabel("Signature class size")
    axis.set_ylabel("Number of classes")
    axis.legend()


def _plot_signatures(axis: Any, before: nx.Graph, after: nx.Graph) -> None:
    before_degrees, after_degrees = dict(before.degree()), dict(after.degree())
    before_triangles, after_triangles = nx.triangles(before), nx.triangles(after)
    axis.scatter(
        [before_degrees[node] for node in before],
        [before_triangles[node] for node in before],
        label="Before",
        alpha=0.7,
    )
    axis.scatter(
        [after_degrees[node] for node in after],
        [after_triangles[node] for node in after],
        label="After",
        alpha=0.7,
    )
    axis.set_xlabel("Degree")
    axis.set_ylabel("Triangle count")
    axis.legend()


def _plot_top_k(axis: Any, comparison: dict[str, Any], width: float) -> None:
    before, after = comparison["ranking"]["before"], comparison["ranking"]["after"]
    ranks = list(range(1, len(before) + 1))
    axis.bar(
        [rank - width / 2 for rank in ranks],
        [item[1] for item in before],
        width,
        label="Before",
    )
    axis.bar(
        [rank + width / 2 for rank in ranks],
        [item[1] for item in after],
        width,
        label="After",
    )
    axis.set_xticks(ranks)
    axis.set_xlabel("Rank")
    axis.set_ylabel("Degree")
    axis.legend()


def write_comparison_figures(
    output_dir: Path,
    before: nx.Graph,
    after: nx.Graph,
    comparison: dict[str, Any],
) -> bool:
    """Create the three requested PNG figures when Matplotlib is available."""
    try:
        import matplotlib
        matplotlib.use("Agg")
        import matplotlib.pyplot as plt
    except ImportError:
        logging.warning("Matplotlib is unavailable; skipping comparison figures.")
        return False

    figures_dir = output_dir / "figures"
    figures_dir.mkdir(parents=True, exist_ok=True)
    figure_specs = (
        ("class_size_histogram.png", lambda axis: _plot_class_sizes(axis, comparison, 0.4)),
        ("degree_vs_triangles.png", lambda axis: _plot_signatures(axis, before, after)),
        ("top_k_degrees.png", lambda axis: _plot_top_k(axis, comparison, 0.4)),
    )
    for filename, draw in figure_specs:
        figure, axis = plt.subplots()
        draw(axis)
        figure.tight_layout()
        figure.savefig(figures_dir / filename, dpi=150)
        plt.close(figure)
    return True
