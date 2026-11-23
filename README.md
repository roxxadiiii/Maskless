# Maskless

**A reproducible study of whether removing names hides structural patterns in a synthetic social network.**

Maskless generates a fictional social graph, replaces the fictional names with anonymous identifiers, and measures a simple two-number node signature:

```text
signature(node) = (degree(node), triangle count(node))
```

The project then applies seeded edge perturbation and compares uniqueness, average clustering, and degree ranking before and after the change.

> Maskless is a privacy-risk indicator, not a re-identification system. A unique signature can make a node structurally distinctive, but it does not prove that the node belongs to a real person.

## Table of contents

- [Introduction](#introduction)
- [Why this project exists](#why-this-project-exists)
- [What Maskless does](#what-maskless-does)
- [Quick start](#quick-start)
- [Installation](#installation)
- [Usage](#usage)
- [Pipeline and methodology](#pipeline-and-methodology)
- [Report and findings](#report-and-findings)
- [Generated artifacts](#generated-artifacts)
- [Privacy and ethics](#privacy-and-ethics)
- [Testing and verification](#testing-and-verification)
- [Project structure](#project-structure)
- [Future work](#future-work)
- [Limitations](#limitations)
- [Contributing](#contributing)
- [License](#license)

## Introduction

Social-network data can expose relationships even when personal names are removed. A name-stripped graph still contains its nodes, edges, degrees, triangles, communities, and other structural patterns. Those patterns may remain distinctive enough to serve as auxiliary knowledge.

Maskless explores this question in a controlled, synthetic setting:

1. Generate an undirected social graph with fictional names.
2. Measure the fraction of nodes whose `(degree, triangle count)` signature occurs exactly once.
3. Relabel every node with a random anonymous identifier.
4. Verify that relabelling preserves the graph and its signatures.
5. Replace a configurable fraction of edges with previously absent edges.
6. Repeat the perturbation across many seeds to describe its variation.
7. Report the measurements and clearly distinguish a possible privacy concern from demonstrated identification.

The project is implemented in Python using NetworkX and the Python standard library. It can run from the repository root with no web service, database, GPU, radio simulation, or real personal data.

## Why this project exists

Name removal is often described as anonymisation, but it is only label replacement. If the topology remains intact, replacing names does not remove:

- node degree;
- participation in triangles;
- connectedness;
- local clustering;
- relative rank or other structural patterns; or
- the correspondence between an observed pattern and an auxiliary description.

The goal of Maskless is to demonstrate, measure, and explain that gap without overstating the result.

In the wireless social-network context, the motivating question is whether graphs derived from proximity, contact events, friend lists, or similar wireless relationships remain distinctive after pseudonyms are applied. The implementation does not model radio propagation, mobility, MAC behavior, or real communities; that context is descriptive only.

## What Maskless does

### Core experiments

- Generates a seeded, undirected, simple NetworkX graph.
- Supports the Holme-Kim `powerlaw_cluster` model and the `barabasi_albert` model.
- Assigns unique, fictional names as node labels.
- Computes degree and triangle-count signatures.
- Measures unique-signature count, unique fraction, distinct signatures, and class-size distribution.
- Produces a seeded bijection from names to identifiers such as `U001`, `U002`, and `U100`.
- Verifies that relabelling preserves node signatures, edge structure, mapped edges, and graph isomorphism.
- Replaces edges on a fresh anonymous graph copy while preserving edge count.
- Compares signature uniqueness, average clustering, top-k degree ranking, transitivity, components, and isolates.
- Repeats the perturbation across a configurable seed sequence on one fixed anonymous base graph.

### Reporting and safety

- Writes machine-readable JSON and CSV results.
- Writes human-readable Markdown tables.
- Generates optional PNG figures with Matplotlib.
- Records configuration, package versions, seeds, timestamps, and execution phases.
- Separates private name/mapping artifacts from shareable graph artifacts.
- Includes explicit limitations and avoids claims of real-world identification.

## Quick start

The default experiment generates 100 nodes and runs 200 robustness perturbations:

```bash
python -m pip install -r requirements.txt
python -m src.main \
  --n 100 \
  --model powerlaw_cluster \
  --m 3 \
  --p 0.5 \
  --seed 42 \
  --rewire 0.10 \
  --topk 5 \
  --robust-runs 200 \
  --out results
```

To include figures:

```bash
python -m pip install -r requirements-plot.txt
python -m src.main --out results
```

To run without Matplotlib:

```bash
python -m src.main --no-plots --out results
```

To run the test suite:

```bash
python -m pip install -r requirements-dev.txt
python -m pytest -q
```

## Installation

### Supported Python versions

The requirements files support Python 3.9 and later. The exact pinned package depends on the Python version.

| Requirement file | Purpose |
|---|---|
| `requirements.txt` | Core runtime dependencies: NetworkX |
| `requirements-plot.txt` | Core dependencies plus Matplotlib |
| `requirements-dev.txt` | Core dependencies plus pytest |

### Standard pip environment

```bash
python -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -r requirements-dev.txt
python -m pip install -r requirements-plot.txt
```

On Windows, activate the environment with:

```powershell
.venv\Scripts\activate
```

Core execution requires only NetworkX and the Python standard library. Matplotlib is optional.

### Arch Linux system package example

The project was also developed with system Python on Arch Linux:

```bash
paru -S python python-networkx python-pytest
```

For figures:

```bash
paru -S python-matplotlib
```

Virtual environments are recommended for general use. They are not required for the original development setup.

## Usage

### Command-line options

```text
python -m src.main [options]
```

| Option | Default | Meaning |
|---|---:|---|
| `--n` | `100` | Number of nodes; must be at least 3 |
| `--model` | `powerlaw_cluster` | `powerlaw_cluster` or `barabasi_albert` |
| `--m` | `3` | Edges added per node; must be between 1 and `n - 1` |
| `--p` | `0.5` | Triad-formation probability for `powerlaw_cluster` |
| `--seed` | `42` | Master seed used to derive stage-specific seeds |
| `--rewire` | `0.10` | Fraction of edges to replace; must be strictly between 0 and 1 |
| `--topk` | `5` | Number of highest-degree nodes to rank |
| `--robust-runs` | `200` | Number of repeated perturbation runs |
| `--out` | `results` | Directory for shareable results |
| `--no-plots` | disabled | Skip PNG figure generation |

### Examples

Smaller graph:

```bash
python -m src.main --n 50 --seed 7 --out results-small
```

Barabasi-Albert graph:

```bash
python -m src.main \
  --n 100 \
  --model barabasi_albert \
  --m 3 \
  --seed 42 \
  --out results-ba
```

More perturbation repetition:

```bash
python -m src.main --rewire 0.20 --robust-runs 500 --out results-20
```

The `--p` parameter applies only to `powerlaw_cluster`.

### Exit codes

| Code | Meaning |
|---:|---|
| `0` | Pipeline completed successfully |
| `1` | Configuration or input error |
| `2` | Internal graph invariant verification failed |

## Pipeline and methodology

### 1. Synthetic network generation

The default generator is `networkx.powerlaw_cluster_graph`:

```text
N = 100
m = 3
p = 0.5
seed = master seed
```

The graph must be an undirected, simple `nx.Graph`. It must contain exactly `N` nodes, have no self-loops or isolated nodes, and contain no node or edge attributes.

### 2. Structural signatures

For node `v`:

```text
degree(v) = G.degree(v)
triangle_count(v) = nx.triangles(G)[v]
signature(v) = (degree(v), triangle_count(v))
```

A signature is unique when it appears once among all nodes. The unique fraction is:

```text
unique fraction = number of nodes with a unique signature / N
```

This is a deliberately weak fingerprint. It discards neighbor identities and most of the graph structure.

### 3. Name removal

Names are fictional labels. They are replaced with shuffled `U###` identifiers using a seeded bijection and `copy=True`.

Maskless verifies:

- the named and anonymous unique counts match exactly;
- the signature multiset is unchanged;
- every mapped per-node signature matches;
- the mapped edge set matches;
- the two graphs are isomorphic.

Relabelling changes labels, not graph topology.

### 4. Edge perturbation

Maskless uses the anonymous graph as the source and creates a fresh perturbed copy.

For edge count `m` and rewire fraction `f`, the replacement count is:

```text
k = int(f * m + 0.5)
```

The pipeline uses round-half-up behavior. It:

- removes `k` existing edges sampled without replacement;
- selects `k` previously absent pairs sampled without replacement;
- creates no self-loops;
- preserves the edge count;
- leaves the source anonymous graph unchanged.

The perturbation is random edge replacement, not degree-preserving rewiring.

### 5. Before-and-after comparison

The primary measurements are:

| Measurement | Meaning |
|---|---|
| Unique fraction | Fraction of nodes with a signature occurring once |
| Average clustering | Mean local clustering coefficient, including zero-valued nodes |
| Top-k ranking | Highest-degree nodes ordered by degree, then identifier |

Supplementary measurements include transitivity, components, isolates, degree movement, exact signature persistence, and distinct signature classes.

### 6. Seeded robustness

Robustness keeps one anonymous base graph fixed. For `R` runs, perturbation seeds begin at:

```text
master_seed + 1000
```

Each run uses `master_seed + 1000 + i`. Summaries use:

- mean;
- population standard deviation (`ddof=0`);
- minimum;
- 5th percentile;
- 95th percentile;
- maximum;
- linear interpolation (type 7) for percentiles.

These values describe variation across perturbations on one base graph. They do not estimate variation across different graph generators or real communities.

## Report and findings

The full academic report is [report/report.md](report/report.md). It includes the problem statement, research questions, formal method, default seed-42 results, privacy interpretation, limitations, viva preparation, and references.

For the reported seed-42 experiment, the written findings include:

- label-only relabelling preserved the 25-node unique-signature count in the 100-node base graph;
- the 10% perturbation replaced 29 edges in the reported 290-edge graph;
- unique fraction changed from 25/100 to 24/100 in the primary perturbation;
- average clustering dropped from `0.3599` to `0.2805`;
- all five top-degree nodes remained in the top five, although the ranking order changed;
- 200 repeated perturbations on the fixed anonymous base graph showed variation rather than a single universal outcome.

These values describe the documented default run. Running the pipeline again with different seeds or parameters may produce different graph sizes and values. Always compare the current machine-readable output and rerun report calculations after changing configuration.

The exact machine-readable source of truth is [results/results.json](results/results.json). Human-readable summaries are in [results/comparison.md](results/comparison.md) and [results/robust.md](results/robust.md).

### Privacy interpretation

The distinctive structural signatures observed illustrate a potential privacy concern. They do not establish that any person can actually be identified, because identification would additionally require accurate auxiliary knowledge, a reliable matching procedure, and a link from an anonymous node to a real individual.

Maskless does not implement:

- an attacker;
- a real auxiliary dataset;
- a ground-truth identity mapping;
- a re-identification attack;
- k-anonymity;
- differential privacy;
- a formal graph privacy guarantee.

## Generated artifacts

Running the pipeline creates shareable and private artifacts.

### Shareable results

| Artifact | Content |
|---|---|
| `results/baseline.json` | Node count, edge count, density, degree, clustering and component statistics |
| `results/uniqueness.json` | Named and anonymous uniqueness statistics |
| `results/relabel_verification.json` | Relabelling invariants and isomorphism check |
| `results/perturbation.json` | Removed edges, added edges, fraction and replacement count |
| `results/comparison.json` | Full before/after comparison |
| `results/comparison.md` | Human-readable comparison table |
| `results/comparison.csv` | Comparison table for spreadsheets |
| `results/robust.json` | All robustness samples and summaries |
| `results/robust.md` | Human-readable robustness summary |
| `results/results.json` | Complete experiment payload |
| `results/G_anon_edges.csv` | Anonymous undirected edge list |
| `results/environment.txt` | Python, NetworkX, configuration and seed metadata |
| `results/run.log` | Timestamped pipeline log |
| `results/figures/*.png` | Optional class-size, signature, and top-k figures |

### Private ground truth

The following directory is ignored by Git:

| Artifact | Content |
|---|---|
| `private/G_named_edges.csv` | Named graph edge list |
| `private/mapping_private.json` | Name-to-anonymous-ID mapping |

Do not share `private/` with anonymous graph releases.

The project also provides separate release archives:

- `dist/maskless-shareable.tar.gz`: source, tests, report, and shareable results;
- `dist/maskless-private.tar.gz`: private mapping and named edge list only.

Keep private and shareable archives separate.

## Privacy and ethics

All names and graph data are synthetic. No real person is targeted. No real personal data is used.

The report's privacy claims are limited to:

1. structural distinctiveness;
2. label invariance;
3. perturbation sensitivity;
4. repeated-run variation;
5. the requirements that would be needed for actual re-identification.

Uniqueness is not proof of identity. A real identification claim would require:

- accurate auxiliary knowledge;
- reliable node matching;
- a link from the matched anonymous identifier to a real individual;
- consideration of false matches;
- evidence from a realistic threat model.

Recommended future mitigation ideas include degree anonymisation, neighbourhood-aware anonymisation, formally analyzed graph perturbation, graph differential privacy, and publishing protected aggregates instead of node-level edges. These mechanisms are outside this project's implemented scope and are not claimed as protections.

## Testing and verification

Run the complete suite:

```bash
python -m pytest -q
```

The tests cover:

- configuration parsing and validation;
- graph generation and baseline invariants;
- signature and uniqueness calculations;
- anonymisation and name leakage;
- relabelling verification;
- edge perturbation;
- before/after comparisons;
- robustness summaries;
- deterministic output;
- documentation requirements;
- verification records.

The maintained verification record is [results/verification.md](results/verification.md).

For a clean rerun, use a dedicated virtual environment, use the pinned requirements, record the environment, and compare outputs only after normalizing timestamps. The run log and `environment.txt` preserve the effective configuration and stage seeds.

## Project structure

```text
Maskless/
├── src/
│   ├── main.py             # CLI orchestration
│   ├── config.py           # CLI and configuration validation
│   ├── generate.py         # Synthetic graph generation
│   ├── names.py            # Fictional name generation
│   ├── signature.py        # Degree/triangle signatures
│   ├── metrics.py          # Uniqueness measurements
│   ├── anonymize.py        # Seeded name relabelling
│   ├── verify.py           # Relabelling invariants
│   ├── perturb.py          # Edge replacement
│   ├── compare.py          # Before/after comparison
│   ├── robust.py           # Repeated perturbation analysis
│   └── report.py           # JSON, CSV, Markdown and figure output
├── tests/                  # Automated test suite
├── results/                # Generated shareable artifacts
├── private/                # Ignored named graph and mapping
├── report/                 # Full Markdown report
├── dist/                   # Shareable and private release archives
├── srs.md                  # Software requirements specification
├── requirements.txt
├── requirements-dev.txt
├── requirements-plot.txt
└── README.md
```

## Future work

Maskless is complete as a synthetic indicator study, but the following extensions would improve scientific coverage:

- [ ] Add Erdős-Rényi, Watts-Strogatz, stochastic-block, and other model sensitivity sweeps.
- [ ] Sweep network size, edge-rewire fraction, top-k size, degree attachment, and triangle probability.
- [ ] Repeat the analysis across many independently generated base graphs.
- [ ] Implement k-degree and k-neighbourhood anonymity for a utility/privacy comparison.
- [ ] Evaluate degree-preserving edge swapping as an alternative perturbation.
- [ ] Add a formal auxiliary-knowledge threat model.
- [ ] Add a concrete but controlled matching experiment with accuracy and false-match analysis.
- [ ] Implement or evaluate differential privacy or a formal graph privacy mechanism.
- [ ] Add temporal, weighted, directed, or multipartite graph support.
- [ ] Add configurable report generation for arbitrary CLI runs.
- [ ] Add a clean-install workflow and continuous integration.
- [ ] Add interactive or web-based exploration if it remains consistent with a real-privacy analysis.
- [ ] Extend the privacy discussion to disclosure, utility, and release policy.

Model and size sensitivity, formal privacy mechanisms, and a real attacker are intentionally out of the current scope rather than silently treated as solved.

## Limitations

- The graph and names are synthetic.
- The main report uses one 100-node `powerlaw_cluster` base graph.
- The signature uses only degree and triangle count.
- The network may not represent real wireless or social-network distributions.
- Edge perturbation is uniform random replacement rather than a formal defense.
- Robustness measures one fixed base graph, not between-network uncertainty.
- Ranking ties depend on identifier-based deterministic sorting.
- No real auxiliary dataset or real identity matching is used.
- Matplotlib is optional; core results do not depend on it.
- A unique signature is a structural indicator, not proof of identification.

## Contributing

Contributions should preserve the project's central boundary:

1. synthetic data only;
2. exact reproducibility;
3. explicit verification;
4. shareable/private artifact separation;
5. cautious privacy language.

For code changes:

1. Create a focused branch.
2. Add or update targeted tests.
3. Run `python -m pytest -q`.
4. Run the default pipeline and verify the reported artifacts.
5. Update this README and the relevant report/SRS text when behavior changes.

Do not commit private mappings, named edge lists, secrets, or real personal data.

## License

Maskless is distributed under the Apache License 2.0. See [LICENSE](LICENSE).
