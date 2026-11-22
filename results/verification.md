# Verification record

Run on 22 November 2026 with system Python `3.14.10`, NetworkX `3.7`, and the default CLI command recorded in `report/report.md`. This file records the evidence behind the Roadmap checkboxes: test results, manual checks, risk mitigations and the residual limitations of the clean-environment check.

## 1. Automated and manual test results

| Check | Method | Result |
|---|---|---|
| Full pytest suite | `python -m pytest -q` | 49 passed in about 2 s; no failures |
| TC-01–TC-40 | Test modules `test_generate`, `test_signature`, `test_metrics`, `test_anonymize`, `test_verify`, `test_perturb`, `test_compare`, `test_robust`, `test_config`, `test_main`, `test_documentation`, `test_report` | Passed |
| TC-41 reproducibility | Automated fixed-timestamp comparison in `test_main`, plus two full runs to the same output directory | Automated pass; manual comparison of 16 files found only timestamp-only differences in `environment.txt`, `results.json` and `run.log`; all three PNGs were byte-identical |
| TC-42 clean Arch system-Python install | Not reproducible in this container: installing packages system-wide is not safe here | Partial: no virtual environment used, pinned requirements present, and a simulated no-Matplotlib run succeeded. A genuinely clean system reinstall remains unverified |
| TC-43 shareable bundle privacy | Manual scan of all 17 shareable files against the 100 private names | No name, `mapping_private.json` or `G_named_edges.csv` found under `results/` |
| TC-44 single-run performance | Two full runs including 200 robustness repetitions | About 4.0 s and 4.1 s; the required under-5-second single-run budget is met |
| TC-45 environment log | Inspect `results/environment.txt` and `results/run.log` | Python, NetworkX, config, all seeds and UTC timestamp present; phase start/finish messages logged |
| TC-46 output files and JSON keys | `test_main` plus manual key audit | All SRS data-dictionary keys present; JSON sorted, indented and UTF-8 |
| TC-47 baseline stats and histogram | `test_generate` plus `results/baseline.json` | Passed |
| TC-48 removal sampling | `test_perturb` | Passed |
| TC-49 generator/size sensitivity | Optional extension not implemented | Not run; recorded as an optional item, not a MUST gap |
| TC-50 report sections | `test_documentation` | Passed |

## 2. Full verification

- **Reproducibility:** two identical commands (`python -m src.main --out /tmp/opencode/repro`) produced identical file lists. After normalising ISO timestamps and log timestamps, `environment.txt`, `results.json` and `run.log` matched; every other file matched byte for byte.
- **Optional dependency:** a `sitecustomize.py` meta-path finder raised `ModuleNotFoundError` for `matplotlib`. The full pipeline still exited 0, logged `WARNING Matplotlib is unavailable; skipping comparison figures.`, wrote no figures directory, and all twelve core modules imported successfully. Core execution needs only NetworkX and the standard library.
- **Artifact validation:** all JSON files parse; both edge CSVs use the header `u,v`; `comparison.csv` uses `Metric,Before,After,Change`; all three PNGs carry a 150 dpi `pHYs` chunk (5906 px/m); Markdown artifacts are non-empty.
- **Privacy scan:** the shareable tree contains 17 files, none containing any of the 100 fictional full names from the private mapping, and no private filenames. The private archive is kept separate from the shareable archive.
- **Citation audit:** six references were checked on 22 November 2026 against publisher-deposited Crossref records via `https://api.crossref.org/works/<DOI>`. Authors, titles, venues, years, page ranges and DOIs agree; the missing page range for Liu and Terzi was added to the report.

## 3. Risk mitigations

| ID | Mitigation actually implemented | Evidence |
|---|---|---|
| R-01 | Model dependence is stated in the report; 200 repeated perturbations summarise variation on the fixed base graph | `report/report.md` Sections 2, 4 and 6; `results/robust.json` |
| R-02 | Unique counts use integers and verification uses exact sorted signature multisets | `src/metrics.py`, `src/verify.py`, `test_verify` |
| R-03 | Identifiers are paired after a seeded shuffle, never in generation order | `src/anonymize.py`, `test_anonymize` |
| R-04 | Names are labels only and a recursive leak check rejects name-bearing attributes | `src/anonymize.py`, `test_anonymize` |
| R-05 | `nx.relabel_nodes(..., copy=True)` and an explicit source-unchanged test | `src/anonymize.py`, `test_anonymize` |
| R-06 | Addition pool comes from `nx.non_edges(G_anon)` on the original graph | `src/perturb.py`, `test_perturb` |
| R-07 | Edges and candidate pairs are normalised and sorted before sampling and output | `src/perturb.py`, `src/main.py`, `test_perturb` |
| R-08 | Ranking is sorted by `(-degree, identifier)`; a rank-k tie flag is reported | `src/compare.py`, `test_compare` |
| R-09 | Mandatory potential-versus-established sentence appears in README and report | `README.md`, `report/report.md`, `test_documentation` |
| R-10 | 200 seeded perturbations precede any spread-based wording | `src/robust.py`, `results/robust.md` |
| R-11 | Dependencies pinned in three requirements files; versions and seeds logged | `requirements*.txt`, `results/environment.txt` |
| R-12 | All MUST phases completed before optional extensions were considered | `Roadmap.md` |
| R-13 | Components and isolates are recorded before and after perturbation | `src/compare.py`, `results/results.json` |

## 4. Edge-case checklist evidence

| Edge case | Evidence |
|---|---|
| No names survive as attributes | Recursive `leak_check` and `test_anonymize` |
| Identifier assignment cannot correlate with generation order | Seeded shuffle in `make_mapping` |
| Relabelling uses no in-place mutation | `copy=True` and source-unchanged assertion |
| Integer/fraction comparisons do not hide mismatches | `unique_stats` counts plus exact multiset comparison |
| k uses half-up rounding, never banker's rounding | `int(f*m + 0.5)`; cases 291→29 and 295→30 tested |
| Edge-list CSV rows are shuffled | `_shuffled_edges` before writing the private CSV |
| Ranking tie behaviour is tie-aware | `_tie_at_k` and `test_compare` |
| Removed edges cannot be re-added | Original-graph non-edge pool |
| Undirected edges are normalised in both directions | Sorted tuple normalisation in `perturb` |
| Post-perturbation isolates/components are reported | `compare.supplementary` |
| Triangle total is per-node sum divided by 3 | `baseline_stats` and handshake/identity tests |
| Average clustering is distinguished from transitivity | Separate metrics; report states the definition |
| Zero/degree-one local clustering reported as 0 | `nx.average_clustering(..., count_zeros=True)` |
| Name pool size checked before generation | `build_names` raises when N exceeds 100 |
| Conclusions are based on robustness, not one draw | Section 4 of the report and `results/robust.md` |

## 5. Data-format checklist evidence

| Requirement | Evidence |
|---|---|
| Edge CSV header `u,v` | `private/G_named_edges.csv`, `results/G_anon_edges.csv` |
| JSON UTF-8, indented, key-sorted | `_write_json` and `test_main` |
| PNG figures | Three PNG files in `results/figures/` |
| Stored floats retain full precision | `results/results.json` uses `json.dumps` defaults |
| Display tables use 4 decimal places | `results/comparison.md` and report tables |
| No `mapping_private.json` in shareable output | Privacy scan and shareable archive listing |
| No `G_named_edges.csv` in shareable output | Privacy scan and shareable archive listing |
| No name node labels or name attributes in shareable output | Privacy scan against all 100 private names |
| Private folder excluded from shareable bundle | `dist/maskless-shareable.tar.gz` contains no `private/` path |

## 6. Residual open items

The following cannot be resolved from the project files and remain author-supplied or course-supplied: roll number, official submission date, required report format/page limit, and whether slides or a demo are required. The instructor name is known from `srs.md` (Dr. Nemi Chandra Rathore) and is recorded in the report's document-control table; the default generator and size are fixed by the SRS. Independent human peer review of the interpretation section is still recommended even though the automated interpretation checks and this self-review passed.

## 7. Filled Appendix D master checklist

- [x] Setup: dependencies pinned; system Python used instead of a virtual environment as requested.
- [x] Repo layout created.
- [x] Config and seeds defined; versions logged.
- [x] N = 100 undirected simple graph.
- [x] Unique fictional names as labels only.
- [x] No self-loops or isolates; components recorded.
- [x] Baseline stats saved.
- [x] `G.degree()` and `nx.triangles()` used.
- [x] Integrity checks pass.
- [x] Unique count and fraction computed.
- [x] Class-size histogram recorded.
- [x] Shuffled `U###` identifiers.
- [x] `relabel_nodes(..., copy=True)`.
- [x] Leakage checks pass.
- [x] Mapping stored privately.
- [x] Counts and multisets identical after relabelling.
- [x] Per-node and edge-set checks pass.
- [x] Negative control fails as it should.
- [x] Verdict line saved.
- [x] Fresh copy; source fingerprint unchanged.
- [x] k computed with round-half-up.
- [x] Added edges drawn from original non-edges.
- [x] Count preserved; no self-loops; disjoint; symmetric difference = 2k.
- [x] Removed and added lists saved.
- [x] Unique fraction before and after.
- [x] Average clustering before and after.
- [x] Top-five lists, overlap, order and tie flag.
- [x] Supplementary indicators.
- [x] Table and figures.
- [x] R repeated runs with summary.
- [ ] Optional generator, size and fraction sweeps (not required for acceptance).
- [x] Mandatory potential-versus-established statement.
- [x] Seven reasons listed.
- [x] Limitations listed.
- [x] Numbers match `results.json`.
- [x] All automated tests green.
- [x] Two same-seed runs identical apart from timestamps.
- [~] Clean-install run works: simulated no-Matplotlib run passed; a clean system reinstall was not performed in this container.
- [x] Bundle has no names.
- [x] Version tagged and archived separately.
