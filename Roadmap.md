# Maskless Implementation Roadmap

## Purpose

This roadmap is the executable to-do list for the course project specified in [srs.md](/home/roxxy/dev/Maskless/srs.md). Complete every item marked **MUST**. Complete SHOULD items unless a reason is recorded. MAY items are optional extensions.

## Status Legend

- `[ ]` Not started
- `[~]` In progress
- `[x]` Complete
- Priority: `M` MUST, `S` SHOULD, `O` MAY

## Delivery Rules

- [x] Treat [srs.md](/home/roxxy/dev/Maskless/srs.md) as the source of truth.
- [x] Use Python 3.9+ and NetworkX 3.x.
- [x] Keep core dependencies limited to NetworkX and the Python standard library.
- [x] Use Matplotlib only as an optional plotting dependency.
- [x] Implement a console application; do not create a GUI, web service, database or wireless-channel simulation.
- [x] Use only synthetic, fictional data.
- [x] Do not implement a real re-identification/de-anonymisation attack or formal privacy mechanism.
- [x] Complete all M items before spending time on S/O items.
- [x] Record every implemented risk mitigation and test result.

## Acceptance Snapshot

- [x] M Generator creates an undirected simple graph with about 100 fictional users.
- [x] M Structural signature is `(G.degree(), nx.triangles())`.
- [x] M Unique-signature fraction is computed before and after relabelling.
- [x] M Anonymisation uses a seeded random bijection and `nx.relabel_nodes(..., copy=True)`.
- [x] M Relabelling invariance is verified by integer count, sorted signature multiset, per-node mapping and mapped edge set.
- [x] M A fresh copy is rewired with exactly the SRS rounding rule for 10% of edges.
- [x] M Perturbation preserves edge count, removes no loops, uses original-graph non-edges and changes exactly `2k` edge-set entries.
- [x] M Uniqueness, average clustering and top-five degree ranking are compared.
- [~] M Machine-readable results and comparison tables are generated; final report artifact is still pending.
- [ ] M The report explicitly says the finding indicates a potential concern, not established identification.
- [x] M Generated shareable results contain no names or private mapping.

# Phase P0 - Setup and Scoping

## P0.1 Requirements and Scope

- [x] `M` Split the project statement into atomic obligations.
- [x] `M` Cover undirected graph, approximately 100 users, degree/triangle signature, unique fraction, relabelling, invariance, fresh copy, 10% rewiring, original absent edges, no self-loops, preserved edge count, three required comparisons and potential-versus-established interpretation.
- [x] `M` Resolve 10% rounding with `k = int(0.10 * m + 0.5)`.
- [x] `M` Resolve ranking ties with `(degree descending, identifier ascending)`.
- [x] `M` Record perturbation source graph as `G_anon`.
- [x] `M` Add no scope items prohibited by Section 1.2.2.

## P0.2 Environment

- [x] `M` Use Arch system Python packages as requested; do not create a virtual environment.
- [x] `M` Add pinned `networkx` dependency.
- [x] `S` Add pinned Matplotlib dependency for figures.
- [x] `S` Add pytest dependency for automated tests.
- [x] `M` Record Python version, NetworkX version, parameters, seeds and timestamp in `results/environment.txt`.
- [x] `M` Record environment and run information in `results/run.log`.

## P0.3 Repository Structure

- [~] `M` Create the repository layout from SRS Section 10.3.
- [x] `M` Add `README.md`, `srs.md`, `requirements.txt`, `Roadmap.md`.
- [x] `M` Add `src/` modules: `config.py`, `names.py`, `generate.py`, `signature.py`, `metrics.py`, `anonymize.py`, `verify.py`, `perturb.py`, `compare.py`, `robust.py`, `report.py`, `main.py`.
- [~] `M` Add focused test modules under `tests/`.
- [x] `M` Create shareable `results/` and private `private/` directories.
- [x] `M` Create `report/` for report and optional slides.
- [x] `M` Keep one responsibility per module and functions reasonably small.
- [~] `M` Add docstrings that explain the concept first and type hints throughout core code.

## P0.4 Configuration and CLI

- [x] `M` Implement one configuration object containing `N`, model name, `M_ATTACH`, `P_TRIAD`, `MASTER_SEED`, `REWIRE_FRACTION`, `TOP_K`, `ROBUST_RUNS` and `OUT_DIR`.
- [x] `M` Set defaults: `N=100`, `m=3`, `p=0.5`, master seed `42`, rewiring fraction `0.10`, top-k `5`, robustness runs `200`, output `results`.
- [x] `M` Implement CLI overrides for `--n`, `--model`, `--m`, `--p`, `--seed`, `--rewire`, `--topk`, `--robust-runs`, `--out` and `--no-plots`.
- [x] `M` Reject `N < 3` with exit code 1.
- [x] `M` Reject rewiring fractions outside `(0,1)`.
- [x] `M` Reject `TOP_K > N` with exit code 1.
- [x] `M` Reject `m >= N` with exit code 1.
- [x] `M` Print clear validation errors.
- [x] `M` Separate random instances for names, anonymisation, perturbation and robustness with seeds derived from one master seed.
- [x] `M` Log every seed and parameter used.
- [x] `M` Record run timestamps while making reproducibility ignore only timestamps.
- [x] `M` Use exit code 0 for success, 1 for validation failure and 2 for internal invariant failure.

## P0.5 Ethics and Privacy Framing

- [x] `M` Document that every user/name is fictional.
- [x] `M` Document that no real person is targeted.
- [x] `M` Document that no re-identification attack is implemented.
- [x] `M` Document that the wireless social-network context is motivational only.
- [~] `M` Put the synthetic-data and ethics statement in `README.md` and the final report.

# Phase P1 - Synthetic Network Generation

## P1.1 Generator Selection

- [x] `M` Implement `nx.powerlaw_cluster_graph(n, m, p, seed)` as the default.
- [x] `M` Make the generator selectable by name (`powerlaw_cluster` or `barabasi_albert`).
- [ ] `O` Implement Erdős-Rényi sensitivity support.
- [ ] `O` Implement Watts-Strogatz sensitivity support.
- [x] `O` Implement Barabási-Albert graph generation support.
- [ ] `O` Implement stochastic-block-model sensitivity support.
- [ ] `S` Explain why Holme-Kim was selected and keep model dependence visible in the report.

## P1.2 Parameters and Baseline

- [x] `M` Default to `N=100`.
- [x] `M` Default to `m=3`.
- [x] `M` Default to `p=0.5`.
- [x] `M` Read actual edge count from the graph; do not hard-code it.
- [x] `M` Record actual edge count, density, degree min/mean/max and degree histogram.
- [x] `M` Record connected components, total triangles, transitivity and average clustering.

## P1.3 Fictional Names

- [x] `M` Build a fixed pool of 10 first names by 10 surnames for exactly 100 unique names.
- [x] `M` Raise a clear error if N exceeds the available pool.
- [x] `M` Sample N names without replacement using the seeded names RNG.
- [x] `M` Map base integer nodes to names by a bijection.
- [x] `M` Store names only as node labels, never node/edge/graph attributes.

## P1.4 Graph Construction

- [x] `M` Create the base graph using the configured generator.
- [x] `M` Relabel the base graph to names with `copy=True`.
- [x] `M` Store the result as `G_named`.

## P1.5 Graph Validation

- [x] `M` Assert `type(G) is nx.Graph`.
- [x] `M` Assert `N` nodes.
- [x] `M` Assert no directed/multi graph representation.
- [x] `M` Assert no self-loops.
- [x] `M` Assert no isolated nodes.
- [x] `M` Assert every node label is a unique string.
- [x] `M` Record component count and whether the graph is connected.
- [x] `M` Fail loudly with exit code 2 for any failed invariant.

## P1.6 Persistence

- [x] `S` Save `G_named_edges.csv` with header `u,v`.
- [x] `S` Shuffle edge-list rows before saving.
- [x] `M` Store `G_named_edges.csv` only under `private/`.
- [x] `M` Never include names in shareable `results/` outputs.

# Phase P2 - Structural Signature Computation

- [x] `M` Compute degrees with `dict(G.degree())`.
- [x] `M` Compute triangle counts with `nx.triangles(G)`.
- [x] `M` Produce `sig[node] = (degree, triangle_count)`.
- [x] `M` Ensure signature values are hashable Python `tuple[int, int]`.
- [x] `M` Assert `sum(degrees) == 2 * edge_count`.
- [x] `M` Assert `sum(triangle_counts) % 3 == 0`.
- [x] `M` Assert `0 <= t(v) <= d(v) * (d(v)-1)/2` for every node.
- [x] `M` Reuse the same signature implementation for named, anonymous and perturbed graphs.
- [ ] `S` Explain that this two-number signature is a weak fingerprint that can still be distinctive.

# Phase P3 - Uniqueness Measurement

- [x] `M` Build `Counter(signature values)`.
- [x] `M` Build the exact unique-node set from signatures occurring once.
- [x] `M` Store unique count as an integer.
- [x] `M` Store unique fraction as `unique_count / N`.
- [x] `M` Use integer counts for equality conclusions.
- [x] `S` Produce signature class-size histogram.
- [x] `S` Record number of distinct signatures and largest class size.
- [x] `S` Record which `(d,t)` values are unique.
- [ ] `S` Check whether unique signatures are associated with higher degrees; report the measured observation, not an expectation.
- [x] `M` Reject an empty graph with a clear error instead of dividing by zero.

# Phase P4 - Anonymisation

- [x] `M` Use identifiers in the form `U` plus a zero-padded integer of width at least 3.
- [x] `M` Create identifiers `U001` through `U100` for the default graph.
- [x] `M` Shuffle identifiers with a seeded RNG before pairing.
- [x] `M` Never assign identifiers according to generation or degree order.
- [x] `M` Create `G_anon = nx.relabel_nodes(G_named, mapping, copy=True)`.
- [x] `M` Preserve `G_named` unchanged.
- [x] `M` Verify the mapping is bijective and all identifiers are unique.
- [x] `M` Verify no original name appears in `G_anon` node labels.
- [x] `M` Verify node, edge and graph attributes contain no names.
- [x] `M` Save `name -> id` mapping only in `private/mapping_private.json`.
- [x] `M` Exclude `private/` from every shareable bundle.

# Phase P5 - Relabelling Verification

- [x] `M` Recompute signatures on `G_anon`.
- [x] `M` Recompute the unique count and fraction on `G_anon`.
- [x] `M` Assert named and anonymous unique counts are exactly identical.
- [x] `M` Assert sorted signature multisets are exactly identical.
- [x] `M` Assert every per-node signature is preserved through `mapping[name]`.
- [x] `M` Assert mapped named edge set equals anonymous edge set.
- [x] `M` Confirm `nx.is_isomorphic(G_named, G_anon)`.
- [x] `M` Emit and save: named count/fraction, anonymous count/fraction and `changed=False`.
- [x] `S` Add a negative control that corrupts `G_anon` and proves verification detects it.
- [~] `M` Explain in code/logs/report that relabelling is an isomorphism and does not alter structure.

# Phase P6 - Edge Perturbation on a Fresh Copy

## P6.1 Fresh Copy

- [x] `M` Create `H = G_anon.copy()`.
- [x] `M` Fingerprint `G_anon` sorted edge set before perturbation.
- [x] `M` Verify the fingerprint is unchanged after perturbation.

## P6.2 Edge Replacement Count

- [x] `M` Calculate `m = G_anon.number_of_edges()`.
- [x] `M` Calculate `k = int(0.10 * m + 0.5)`.
- [x] `M` Log `m`, `k` and the rounding rule.
- [x] `M` Do not use Python banker's rounding.
- [x] `M` Test `m=291 -> k=29`.
- [x] `M` Test `m=295 -> k=30`.

## P6.3 Removal

- [x] `M` Normalize all existing edges to sorted undirected tuples.
- [x] `M` Sort edge tuples for deterministic iteration.
- [x] `M` Sample exactly `k` existing edges without replacement.
- [x] `M` Remove them from `H` only.

## P6.4 Addition

- [x] `M` Evaluate `nx.non_edges(G_anon)` on the original graph.
- [x] `M` Normalize candidates to sorted tuple pairs and sort them.
- [x] `M` Exclude every original edge and every self-loop.
- [x] `M` Exclude removed edges from re-addition.
- [x] `M` Sample exactly `k` candidates without replacement.
- [x] `M` Remove first, then add all selected edges.

## P6.5 Postconditions

- [x] `M` Assert edge count is preserved.
- [x] `M` Assert no self-loops exist.
- [x] `M` Assert no duplicate edges exist.
- [x] `M` Assert every added edge was absent in `G_anon`.
- [x] `M` Assert removed and added sets are disjoint.
- [x] `M` Assert symmetric difference is exactly `2k`.
- [x] `M` Assert node set is unchanged.
- [x] `M` Assert `G_anon` edge set is unchanged.
- [x] `M` Persist normalized removed and added edge lists.
- [x] `M` Document that degree sequence may change, triangles may change and connectedness may change.

# Phase P7 - Before/After Comparison

## P7.1 Signature Uniqueness

- [x] `M` Calculate named/anonymous unique count and fraction before perturbation.
- [x] `M` Calculate perturbed unique count and fraction.
- [x] `M` Report absolute difference in percentage points.
- [x] `M` Use exact integer comparison for unique-count invariance.

## P7.2 Average Clustering

- [x] `M` Compute average clustering with `nx.average_clustering(G, count_zeros=True)`.
- [x] `M` Report before value, after value, absolute change and relative change.
- [x] `M` Label this as the mean of local clustering coefficients, not transitivity.

## P7.3 Top-Five Degree Ranking

- [x] `M` Rank nodes by `(-degree, identifier)`.
- [x] `M` Report five `(id, degree)` pairs before and after.
- [x] `M` Report overlap count from 0 to 5.
- [x] `M` Report whether ranking order is identical.
- [x] `M` Report rank movement for every node.
- [x] `M` Detect and report whether the rank-5 position is tied with rank 6.
- [x] `M` Avoid relabelling tie artefacts in ranking comparisons.

## P7.4 Supplementary Indicators

- [x] `S` Record number of distinct signatures before and after.
- [x] `S` Record largest signature class before and after.
- [x] `S` Record class-size histogram before and after.
- [x] `S` Record fraction of originally unique nodes whose signature remains unchanged.
- [x] `S` Record fraction of originally unique nodes that remain unique.
- [x] `S` Record number of nodes whose signature changed.
- [x] `S` Record transitivity before and after.
- [x] `S` Record connected-component count before and after.
- [x] `S` Summarize degree-sequence differences.
- [x] `S` Record isolated nodes before and after perturbation.

## P7.5 Outputs

- [x] `M` Create one comparison table with Before, After and Change columns.
- [x] `S` Create a class-size histogram figure.
- [x] `S` Create a degree-versus-triangles scatter figure.
- [x] `S` Create a top-five degree bar/line chart.
- [x] `S` Save figures as PNG at 150 dpi or higher.

# Phase P8 - Robustness and Sensitivity

## P8.1 Repeated Perturbation

- [x] `S` Keep the base graph fixed.
- [x] `S` Repeat P6/P7 for 200 perturbation seeds by default.
- [x] `S` Use `Random(master_seed + 1000 + i)` or an equally documented derived sequence.
- [x] `S` Summarize unique fraction after rewiring.
- [x] `S` Summarize average clustering after rewiring.
- [x] `S` Summarize top-five overlap.
- [x] `S` Report mean, standard deviation, minimum, 5th percentile, 95th percentile and maximum.
- [x] `S` Word conclusions according to the observed spread in `results/robust.md`, limiting interpretation to perturbation variation on the fixed base graph.

## P8.2 Repeated Base Graphs

- [ ] `O` Repeat P1-P7 across multiple base seeds.
- [ ] `O` Report between-base variation separately from within-base perturbation variation.

## P8.3 Generator Sensitivity

- [ ] `O` Run the pipeline with Erdős-Rényi.
- [ ] `O` Run the pipeline with Watts-Strogatz.
- [ ] `O` Run the pipeline with Barabási-Albert.
- [ ] `O` Run the pipeline with stochastic block model.
- [ ] `O` Test whether near-regular graphs produce fewer unique signatures.
- [ ] `O` Test whether heavy-tailed graphs produce more unique signatures.
- [ ] `O` Save sensitivity results and explain that conclusions are model-dependent.

## P8.4 Size Sensitivity

- [ ] `O` Run sensitivity checks for `N=50`.
- [ ] `O` Run sensitivity checks for `N=100`.
- [ ] `O` Run sensitivity checks for `N=200`.
- [ ] `O` Analyze how uniqueness changes with graph size.

## P8.5 Rewiring-Fraction Sweep

- [ ] `O` Test `f=0`.
- [ ] `O` Test `f=0.01`.
- [ ] `O` Test `f=0.05`.
- [ ] `O` Test `f=0.10`.
- [ ] `O` Test `f=0.20`.
- [x] `M` Verify `f=0` exactly reproduces the baseline graph and metrics.

# Phase P9 - Interpretation and Privacy Discussion

- [x] `M` Report the actual measured values; do not turn expectations into findings.
- [x] `M` State relabelling did not change the unique fraction.
- [x] `M` State exactly how uniqueness, clustering and top-five ranking changed after rewiring.
- [x] `M` Explain that naïve anonymisation hides labels, not topology.
- [x] `M` Explain that rewiring makes exact auxiliary signatures less reliable.
- [x] `M` Explain that perturbation is not a formal privacy guarantee.
- [x] `M` Explain the utility cost: clustering/ranking drift and possible utility loss.
- [x] `M` Include the mandatory potential-versus-established sentence.
- [x] `M` Include all seven mandatory reasons why distinctive signatures do not establish identification.
- [x] `S` Discuss k-degree anonymity as a mitigation pointer only.
- [x] `S` Discuss k-neighbourhood anonymity as a mitigation pointer only.
- [x] `S` Discuss formal edge-perturbation analysis as a mitigation pointer only.
- [x] `S` Discuss differential privacy for graph statistics as a mitigation pointer only.
- [x] `S` Discuss releasing aggregates instead of graphs.
- [x] `M` List limitations: synthetic data, one generator, two-number signature, N around 100, random rewiring and no attacker model.
- [x] `M` Never claim actual identification in the report.

# Phase P10 - Deliverables and Reporting

## P10.1 Source and README

- [x] `M` Ensure all source code is runnable and documented.
- [x] `M` Document setup and the exact CLI in `README.md`.
- [x] `M` Document expected output files and interpretation statement.
- [x] `M` Document private/shareable file handling.

## P10.2 Results Data

- [x] `M` Write `results/results.json`.
- [x] `M` Store UTF-8, indented and sorted JSON keys.
- [x] `M` Preserve full float precision in JSON.
- [x] `M` Show 4 decimal places only in human-readable tables.
- [x] `M` Write `results/comparison.md`.
- [x] `M` Write `results/comparison.csv`.
- [x] `M` Write `results/run.log`.
- [x] `M` Write `results/G_anon_edges.csv`.
- [x] `M` Write `results/environment.txt`.
- [x] `M` Include every key listed in the SRS results data dictionary.
- [x] `M` Save robustness summaries under `robust.*` when P8.1 runs.
- [x] `M` Save removed and added edge lists in perturbation results.

## P10.3 Figures

- [x] `S` Generate figures from the pipeline, not typed manually.
- [x] `S` Save PNG files under `results/figures/`.
- [x] `S` Preserve a useful resolution of at least 150 dpi.

## P10.4 Written Report

- [x] `M` Create `report/report.md`.
- [x] `M` Write a 150-word abstract.
- [x] `M` Cover title, introduction and wireless-social-network motivation.
- [x] `M` State problem statement and research questions.
- [x] `M` Explain method: generator, signature, uniqueness, relabelling, perturbation and metrics.
- [x] `M` Explain ELI5/analogy before formulas.
- [x] `M` Summarize implementation and reproducibility.
- [x] `M` Report baseline graph statistics.
- [x] `M` Report relabelling verdict.
- [x] `M` Report anonymised-versus-perturbed comparison table.
- [x] `M` Report robustness findings and model sensitivity if implemented.
- [x] `M` Include mandatory privacy interpretation and all limitations.
- [x] `M` Include mitigation pointers.
- [x] `M` Write conclusion.
- [ ] `M` Verify reference details and citations against each publisher's original record before submission; DOI metadata has been cross-checked, but this final source audit remains.
- [ ] `M` Export PDF or DOCX if required by the course.
- [x] `M` Add seeds, versions, CLI command and full tables in an appendix.
- [x] `M` Add git hash or commit identifier if available; note that the tree was dirty.

## P10.5 Slides

- [ ] `O` Create `report/slides.md` or the course-required slide format.
- [ ] `O` Use 8-10 slides.
- [ ] `O` Include question, wireless motivation, network/signature, uniqueness, relabelling, rewiring, comparison, robustness, potential-versus-established and takeaways.

## P10.6 Viva Preparation

- [x] `S` Prepare why relabelling does not change uniqueness.
- [x] `S` Prepare why degree and triangles are used.
- [x] `S` Prepare what `nx.triangles` returns.
- [x] `S` Prepare why identifiers are shuffled.
- [x] `S` Prepare why new edges come from original non-edges.
- [x] `S` Prepare whether rewiring preserves degrees.
- [x] `S` Prepare why clustering may change.
- [x] `S` Prepare whether a unique signature is a privacy breach.
- [x] `S` Prepare whether perturbation is a real defense.
- [x] `S` Prepare how results may change with another generator.
- [x] `S` Prepare how a tie at rank 5 is handled.
- [x] `S` Prepare how reproducibility is ensured.

# Phase P11 - Quality Assurance and Closure

## P11.1 Automated Test Suite

- [x] `M` TC-01 assert graph type.
- [x] `M` TC-02 assert node count.
- [x] `M` TC-03 assert unique string names.
- [x] `M` TC-04 assert no name attributes.
- [x] `M` TC-05 assert no loops or isolates.
- [x] `M` TC-06 assert generation determinism.
- [x] `M` TC-07 assert signature tuple types.
- [x] `M` TC-08 verify handshake lemma.
- [x] `M` TC-09 verify triangle identity.
- [x] `M` TC-10 verify triangle upper bound.
- [x] `M` TC-11 verify uniqueness on a path of 4 nodes.
- [x] `M` TC-12 verify uniqueness on a 5-leaf star.
- [x] `M` TC-13 verify uniqueness on a 10-node cycle.
- [x] `M` TC-14 verify an empty graph raises an error.
- [x] `M` TC-15 verify mapping bijection.
- [x] `M` TC-16 verify identifier format.
- [x] `M` TC-17 verify relabel source graph remains unchanged.
- [x] `M` TC-18 verify anonymisation has no name leakage.
- [x] `M` TC-19 verify unique-count invariance.
- [x] `M` TC-20 verify signature-multiset invariance.
- [x] `M` TC-21 verify per-node mapped signatures.
- [x] `M` TC-22 verify mapped edge set and isomorphism.
- [x] `S` TC-23 verify negative-control relabelling corruption is detected.
- [x] `M` TC-24 verify the source graph fingerprint survives perturbation.
- [x] `M` TC-25 verify k rounding.
- [x] `M` TC-26 verify edge count preservation.
- [x] `M` TC-27 verify no loops or duplicate edges.
- [x] `M` TC-28 verify added edges are original absent edges.
- [x] `M` TC-29 verify removed/added disjointness and symmetric difference.
- [x] `M` TC-30 verify node set preservation.
- [x] `M` TC-31 verify `f=0` is an identity operation.
- [x] `M` TC-32 cross-check average clustering to manual local-coefficient mean.
- [x] `M` TC-33 verify top-five determinism.
- [x] `M` TC-34 verify rank-5 tie flag.
- [x] `S` TC-35 verify uniqueness-persistence metric.
- [x] `M` TC-36 verify comparison table completeness.
- [x] `S` TC-37 verify robustness summary statistics.
- [x] `M` TC-38 verify mandatory interpretation sentence in report.
- [x] `M` TC-39 verify limitations section in report.
- [x] `M` TC-40 verify CLI validation exit code 1.
- [x] `M` TC-41 verify whole-run reproducibility apart from timestamp.
- [ ] `M` TC-42 verify a clean Arch system-Python package installation, without creating a virtual environment (per user setup requirement).
- [x] `M` TC-43 verify shareable bundle privacy hygiene.
- [x] `M` TC-44 verify single-run performance under 5 seconds.
- [x] `M` TC-45 verify environment log completeness.
- [x] `M` TC-46 verify output files and JSON keys.
- [x] `M` TC-47 verify baseline stats and class-size histogram.
- [x] `M` TC-48 verify removal sample size and uniformity.
- [ ] `O` TC-49 verify sensitivity runs execute for each supported generator.
- [x] `M` TC-50 verify report sections against the SRS outline.

## P11.2 Full Verification

- [x] `M` Run the full test suite.
- [ ] `M` Ensure every MUST test passes.
- [x] `M` Run the pipeline twice with the same seed.
- [x] `M` Diff outputs and ignore only timestamp differences.
- [x] `M` Ensure all seeds and versions are logged.
- [x] `M` Scan `results/` for names and private fields.
- [x] `M` Scan `private/` and keep it out of submission bundle.
- [x] `M` Validate all JSON and CSV outputs.
- [x] `M` Validate Markdown and PNG artifacts.

## P11.3 Clean Environment

- [ ] `M` Verify from a clean supported Python/Arch package setup without creating a virtual environment.
- [ ] `M` Install from `requirements.txt`.
- [ ] `M` Run tests in the clean environment.
- [ ] `M` Run the full pipeline in the clean environment.
- [ ] `M` Verify no optional package is required by core execution.
- [ ] `M` Verify Matplotlib absence produces a warning and not a crash.

## P11.4 Report Review

- [ ] `M` Peer-read the interpretation section.
- [x] `M` Confirm no identification claim is made.
- [x] `M` Confirm every reported number matches `results.json`.
- [x] `M` Confirm the k rounding rule is stated.
- [x] `M` Confirm generator and parameters are stated.
- [x] `M` Confirm all limitations are stated.
- [ ] `M` Confirm citations are verified.

## P11.5 Closure

- [ ] `M` Complete Appendix D master checklist.
- [ ] `M` Fill in all Appendix E result placeholders.
- [ ] `M` Resolve or document Appendix F open items.
- [ ] `M` Tag the final version.
- [ ] `M` Archive private and shareable bundles separately.
- [ ] `M` Export and verify the final report.
- [ ] `M` Rehearse viva answers.

# Risk and Loophole Register

- [ ] `M/R-01` Keep model dependence explicit and run robustness/sensitivity where time allows.
- [ ] `M/R-02` Compare integer counts and exact signatures; never use float equality for invariance.
- [ ] `M/R-03` Prevent identifier-order leakage with seeded random bijection.
- [ ] `M/R-04` Prevent name attributes from surviving anonymisation.
- [ ] `M/R-05` Always use `copy=True` for relabelling.
- [ ] `M/R-06` Draw additions from original non-edges to prevent removed-edge re-addition.
- [ ] `M/R-07` Sort all edge and node iteration-sensitive inputs and outputs.
- [ ] `M/R-08` Flag rank-5 ties and avoid false ranking-change claims.
- [ ] `M/R-09` Include mandatory potential-versus-established language and review it.
- [ ] `M/R-10` Use repeated perturbations before generalising from one random draw.
- [ ] `M/R-11` Pin dependencies and log exact versions.
- [ ] `M/R-12` Complete MUST work before SHOULD/MAY extensions.
- [ ] `M/R-13` Report component and isolate changes after rewiring.

# Edge-Case Checklist

- [ ] `M` No names survive as attributes.
- [ ] `M` Identifier assignment cannot correlate with generation order.
- [ ] `M` Relabelling uses no in-place mutation.
- [ ] `M` Integer/fraction comparisons do not hide mismatches.
- [ ] `M` k uses half-up rounding, never banker's rounding.
- [ ] `M` Edge-list CSV rows are shuffled.
- [ ] `M` Ranking tie behaviour is tie-aware.
- [ ] `M` Removed edges cannot be re-added.
- [ ] `M` Undirected edges are normalized in both directions.
- [ ] `M` Post-perturbation isolates/components are reported.
- [ ] `M` Triangle total is computed by summing per-node counts and dividing by 3.
- [ ] `M` Average clustering is distinguished from transitivity.
- [ ] `M` Zero-degree/degree-one local clustering is reported as 0.
- [ ] `M` Name pool size is checked before graph generation.
- [ ] `M` Conclusions are based on robustness, not one perturbation sample.

# Data-Format and Output Checklist

- [ ] `M` Edge CSV header is `u,v`.
- [ ] `M` JSON is UTF-8, indented and key-sorted.
- [ ] `M` PNG is used for figures.
- [ ] `M` Stored floats retain full precision.
- [ ] `M` Display tables use 4 decimal places.
- [ ] `M` Shareable output never contains `mapping_private.json`.
- [ ] `M` Shareable output never contains `G_named_edges.csv`.
- [ ] `M` Shareable output never contains name node labels or name attributes.
- [ ] `M` Private folder is kept out of `results/` and final submission bundle.

# Report Results Template

- [ ] `M` Fill network model, N, m, average degree, components, triangles and average clustering.
- [ ] `M` Fill named and anonymised unique counts/fractions.
- [ ] `M` Fill perturbation m, k, rounding rule and seeds.
- [ ] `M` Fill before/after unique count/fraction.
- [ ] `M` Fill before/after average clustering and change.
- [ ] `M` Fill before/after transitivity and components.
- [ ] `M` Fill distinct-signature and largest-class values.
- [ ] `M` Fill unique-signature persistence values.
- [ ] `M` Fill top-five `(id, degree)` pairs for both graphs.
- [ ] `M` Fill top-five overlap, same-order and tie-at-rank-5 values.
- [ ] `S` Fill robustness mean, SD, min, 5th percentile, 95th percentile and max.
- [ ] `M` Copy the measured, not prewritten, interpretation statement into the report.

# Open Items

- [ ] `M` Fill instructor name.
- [ ] `M` Fill roll number.
- [ ] `M` Fill official submission date.
- [ ] `M` Confirm required report format and page limits.
- [ ] `M` Confirm whether the course requires slides or a demo.
- [ ] `M` Confirm whether it requires a specific generator or network size.
- [ ] `M` Verify all original literature references.
- [ ] `M` Replace every blank with actual run values.