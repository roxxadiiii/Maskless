# Structural Distinctiveness in a Synthetic Social Network

| Field | Value |
|---|---|
| Course | Wireless Social Network |
| Programme | M.Sc. Artificial Intelligence, Central University of South Bihar (CUSB) |
| Author | Aditya Kumar |
| Instructor | Dr. Nemi Chandra Rathore |
| Roll number | To be supplied by the author |
| Submission date | To be supplied by the author |
| Report date | 22 November 2026 |

## Abstract

Anonymising a social network by replacing names may leave structural patterns intact. This study tests that question on a synthetic undirected graph of 100 fictional users generated with the powerlaw-cluster model. Each node is represented by its degree and triangle count; uniqueness is the fraction whose pair occurs once. A seeded bijection replaces names with identifiers, and checks test invariance. An anonymised copy then undergoes 10% edge replacement using pairs absent from the original graph, preserving edge count. For seed 42, 25 of 100 signatures were unique before and after relabelling. Rewiring 29 of 290 edges reduced uniqueness to 24 nodes and average clustering from 0.3599 to 0.2805; top-five membership remained 5/5, but order changed. Across 200 perturbations of one base graph, unique fraction ranged from 0.12 to 0.30. These findings indicate potential structural privacy concerns in this controlled synthetic experiment, not real-world identification, attack success, or a privacy guarantee.

## 1. Introduction and motivation

Wireless social-network applications can represent people or devices as nodes and relationships or communication links as edges. Removing names from such a graph may not remove its structure. A node's local pattern can remain distinctive, which motivates studying structural privacy before publishing network data. Prior work has examined structural re-identification and graph anonymisation [1–4]. This project uses only generated data: its wireless-network framing is motivational, and it does not simulate radios, mobility, or a real community.

### Problem statement

This study asks whether replacing names with anonymous identifiers changes the uniqueness of a simple structural signature, and how a seeded 10% edge-replacement operation changes signature uniqueness, average clustering, and the top-five degree ranking. It also measures how those perturbation outcomes vary across repeated seeds while holding one base graph fixed.

### Research questions

1. Does label-only anonymisation change the fraction of unique `(degree, triangle count)` signatures?
2. What changes in signature uniqueness, average clustering, and the top-five degree ranking after 10% edge replacement?
3. How much do those three post-perturbation measurements vary over 200 perturbation seeds on the same base graph?

## 2. Method

### ELI5: name tags and two-number fingerprints

Imagine a club represented by a map: people are dots and friendships are lines. Each person gets a two-number fingerprint: their number of friends and the number of friend-triangles they participate in. Replacing a person's name tag with a random code changes the label, not the map or fingerprint. Rewiring some friendship lines changes the map and can change fingerprints. A fingerprint that appears once is distinctive within this particular map; it is not, by itself, proof of who the person is.

### Formal method

The default graph is an undirected, simple `powerlaw_cluster_graph` generated with `N=100`, attachment parameter `m=3`, triad probability `p=0.5`, and seed `42`. For each node `v`, the signature is `s(v) = (degree(v), triangles(v))`. A signature is unique when its frequency in the graph equals one; the unique fraction is the number of such nodes divided by `N`.

Fictional names are replaced by a seeded random bijection to `U###` labels using a fresh graph copy. Verification compares exact unique counts and signature multisets, mapped per-node signatures, mapped edges, and graph isomorphism. The perturbation is then applied to a fresh copy of the anonymous graph. For `m_e` edges and fraction `f=0.10`, the replacement count is `k = int(f * m_e + 0.5)`. Removed edges are sampled without replacement from existing edges; added edges are sampled without replacement from pairs absent in the original graph. The original graph is not modified, and the total edge count is preserved.

The Holme–Kim generator was selected as the default because it combines a heavy-tailed degree distribution with triad formation, producing varied signatures while remaining a simple, seeded NetworkX call. Results are therefore model-dependent: another generator may produce a different unique fraction. The signature is deliberately weak, since degree and triangle count ignore who the neighbours are, yet even this two-number fingerprint can already be distinctive.

Before/after metrics are: unique-signature count and fraction, average local clustering coefficient (including zero values), and top-five degree ranking with deterministic identifier-based tie-breaking. Supplemental measures include transitivity, component count, rank movement, and signature persistence. Robustness holds `G_anon` fixed and repeats perturbation and comparison for 200 seeds beginning at `master_seed + 1000`; summaries use population standard deviation (`ddof=0`) and linearly interpolated type-7 percentiles.

## 3. Implementation and reproducibility

The pipeline is implemented in Python with NetworkX. Separate random seeds isolate graph generation, fictional-name assignment, anonymisation, the primary perturbation, and robustness runs. Edge candidates are sorted before sampling to keep runs deterministic. Automated tests cover configuration, invariants, calculations, outputs, and seeded robustness. The shareable outputs exclude the private name-to-identifier mapping and named graph edge list.

For the reported default run, the environment was Python `3.14.10` and NetworkX `3.7`. The command was:

```bash
python -m src.main --n 100 --model powerlaw_cluster --m 3 --p 0.5 \
  --seed 42 --rewire 0.10 --topk 5 --robust-runs 200 --out results
```

The stage seeds were master `42`, names `43`, anonymisation `44`, primary perturbation `45`, and robustness seeds `1042` through `1241`. Full precision data and parameters are in [`results.json`](../results/results.json); execution outputs and environment metadata are in `results/`.

## 4. Results

### Baseline graph

The generated graph had 100 nodes and 290 edges, density `0.0586`, mean degree `5.8`, minimum degree `3`, maximum degree `33`, and 152 triangles. It was connected (one component). Baseline average clustering was `0.3599`; transitivity was `0.1806`.

### Relabelling

Before relabelling, 25 of 100 nodes (`0.25`) had unique signatures. After relabelling, the count and fraction were still 25 and `0.25`. Per-node signatures, the signature multiset, and the mapped edge set matched, and the graphs were isomorphic. Thus, for this run, replacing labels alone did not change structural uniqueness. Unique signatures were associated with higher degree in this graph: the 25 unique nodes had mean degree `11.64` versus `5.80` across all nodes, all 13 nodes with degree at least 10 were unique, and 12 of the remaining 87 nodes (`13.8%`) were unique. This is a measured observation for this base graph, not an expected result.

### Primary perturbation comparison

The run replaced 29 of 290 edges, preserving the edge count.

| Metric | Before | After | Change |
|---|---:|---:|---:|
| Unique signature count | 25 | 24 | -1 |
| Unique fraction | 0.2500 | 0.2400 | -1.0000 percentage point |
| Average clustering | 0.3599 | 0.2805 | -0.0794 (-22.0562%) |
| Top-five degree ranking | U051:33, U079:23, U055:20, U050:17, U089:17 | U051:30, U055:20, U079:19, U050:17, U089:15 | Overlap 5/5; order changed; no rank-five tie |

The top-five membership stayed the same, but the second and third positions switched: `U079` and `U055`. There was no tie at rank five in either graph. In the supplementary measures, 69 nodes changed signature; of the 25 nodes unique before perturbation, 3 retained the exact signature and 17 remained unique. The graph remained connected with no isolates. These observations describe this one perturbation draw, not a universal effect.

### Repeated perturbations

With the same anonymous base graph and 200 distinct perturbation seeds, the results were:

| Post-perturbation metric | Mean | Population SD | Min | 5th pct | 95th pct | Max |
|---|---:|---:|---:|---:|---:|---:|
| Unique fraction | 0.2322 | 0.0303 | 0.1200 | 0.1800 | 0.2800 | 0.3000 |
| Average clustering | 0.2681 | 0.0178 | 0.2072 | 0.2400 | 0.2965 | 0.3160 |
| Top-five overlap (count) | 4.3300 | 0.5487 | 3 | 4.0000 | 5.0000 | 5 |

The measures varied across perturbations, so the single-run values should not be treated as inevitable. These distributions quantify only perturbation-to-perturbation variation for this fixed graph and seed sequence; they do not capture variation across base graphs or generators.

## 5. Privacy interpretation

**The distinctive structural signatures observed illustrate a potential privacy concern. They do not establish that any person can actually be identified, because identification would additionally require accurate auxiliary knowledge, a reliable matching procedure, and a link from an anonymous node to a real individual.** This project measures structural distinctiveness, not identity disclosure or attack success.

Replacing names with random identifiers hides labels, but it does not hide topology: the same edges and signatures remain. In the primary perturbation, exact signature matches became less stable, and clustering and rank order drifted. This suggests that exact auxiliary signatures may be less reliable after this particular perturbation, but it does not provide a formal privacy guarantee. The observed clustering change and ranking movement also demonstrate a utility cost; preserving edge count alone does not preserve every graph property.

The following reasons prevent treating uniqueness as proof of identification:

1. **Auxiliary knowledge is required.** An observer would need the target's exact degree and triangle count; such information may not be available.
2. **Exactness is fragile.** Small edge changes alter signatures. Inaccurate auxiliary knowledge can produce mismatches or false matches.
3. **Uniqueness is graph-relative.** A signature unique among these 100 generated nodes may be common in a larger graph, and a real target may not be represented at all.
4. **Structure is not identity.** A match points to an anonymous node such as `U047`, not to a real person; linking them requires additional external information.
5. **A necessary, not sufficient, condition.** Here uniqueness is only a screening indicator. Identification requires an actual matching procedure and evidence that the match is correct.
6. **The data are synthetic.** Results from one generator do not establish the risk in any real community.
7. **Risk is probabilistic.** The supported conclusion is a potential concern deserving careful assessment, not that individuals are identifiable.

### Mitigation pointers

These are directions for further study, not protections evaluated or guaranteed by this project:

- **k-degree anonymity:** generalize or modify degree patterns so a node's degree is shared by a group [4].
- **k-neighbourhood anonymity:** consider the larger local neighbourhood, not only one degree value; graph anonymisation methods require careful utility and threat-model evaluation [3].
- **Formally analyzed edge perturbation:** define an attacker and privacy notion, then prove or measure the guarantee; random rewiring alone is not such an analysis.
- **Differential privacy for graph statistics:** calibrate noise to a stated adjacency model and sensitivity; differential privacy is a formal framework, not a property inherited by this release [6].
- **Release aggregates instead of an individual-level graph:** where possible, publish appropriately protected summaries rather than node-level edges.

## 6. Limitations

- The graph and names are synthetic; no real personal data or community was studied.
- The reported experiment uses one `powerlaw_cluster` base graph. Optional generator, size, and repeated-base sensitivity sweeps were not run.
- The signature uses only two local features: degree and triangle count.
- The network has 100 nodes; results need not scale to larger or smaller graphs.
- Rewiring is simple random edge replacement and has no formal privacy analysis.
- No attacker, real auxiliary dataset, identity matching, or ground-truth identification experiment was implemented.
- The 200-run robustness analysis fixes one base graph, so it does not estimate between-network uncertainty.
- The wireless-social-network setting is a motivation only; there is no radio, mobility, or communication simulation.

## 7. Conclusion

In this seeded synthetic example, label replacement preserved the unique-signature fraction exactly, while replacing 10% of the edges reduced it by one percentage point and lowered average clustering by about 22%. The top-five set remained unchanged, although its order shifted. Repeated perturbations showed meaningful variation on the fixed base graph. Together, the results support caution about releasing name-stripped graphs and show a measurable utility trade-off, but they do not establish real-person identification or a formal privacy guarantee. Broader claims require additional generators, base graphs, threat models, and formal privacy analysis.

## References

**Source audit completed 22 November 2026.** Each entry was checked against its publisher-deposited Crossref record (`https://api.crossref.org/works/<DOI>`). Authors, title, venue, year, page range and DOI agree with the records consulted; the page range for reference 4 was added from that record. This audit confirms bibliographic metadata, not that every cited claim was re-read in full.

1. L. Backstrom, C. Dwork, and J. Kleinberg. “Wherefore Art Thou R3579X?: Anonymized Social Networks, Hidden Patterns, and Structural Steganography.” *Proceedings of the 16th International World Wide Web Conference*, 2007, pp. 181–190. [doi:10.1145/1242572.1242598](https://doi.org/10.1145/1242572.1242598).
2. A. Narayanan and V. Shmatikov. “De-anonymizing Social Networks.” *2009 IEEE Symposium on Security and Privacy*, pp. 173–187. [doi:10.1109/SP.2009.22](https://doi.org/10.1109/SP.2009.22).
3. M. Hay, G. Miklau, D. Jensen, D. Towsley, and P. Weis. “Resisting Structural Re-identification in Anonymized Social Networks.” *Proceedings of the VLDB Endowment*, 1(1), 2008, pp. 102–114. [doi:10.14778/1453856.1453873](https://doi.org/10.14778/1453856.1453873).
4. K. Liu and E. Terzi. “Towards Identity Anonymization on Graphs.” *Proceedings of the 2008 ACM SIGMOD International Conference on Management of Data*, 2008, pp. 93–106. [doi:10.1145/1376616.1376629](https://doi.org/10.1145/1376616.1376629).
5. L. Sweeney. “k-Anonymity: A Model for Protecting Privacy.” *International Journal of Uncertainty, Fuzziness and Knowledge-Based Systems*, 10(5), 2002, pp. 557–570. [doi:10.1142/S0218488502001648](https://doi.org/10.1142/S0218488502001648).
6. C. Dwork. “Differential Privacy.” In *Automata, Languages and Programming (ICALP 2006)*, Part II, Lecture Notes in Computer Science 4052, 2006, pp. 1–12. [doi:10.1007/11787006_1](https://doi.org/10.1007/11787006_1).

## Appendix A. Run details

- Python: `3.14.10`; NetworkX: `3.7`.
- Configuration and seeds: see `results/results.json` and `results/environment.txt`.
- Master seed: `42`; perturbation seed: `45`; robustness seeds: `1042–1241`.
- Command: `python -m src.main --n 100 --model powerlaw_cluster --m 3 --p 0.5 --seed 42 --rewire 0.10 --topk 5 --robust-runs 200 --out results`.
- The source release is tagged `v1.0.0`; the generated report and results are delivered in `dist/maskless-shareable.tar.gz` because `report/` and `results/` are intentionally Git-ignored. The pre-closure draft HEAD was `a096042` with a dirty tree, so that hash is not a release identifier.
- The complete machine-readable measurements are in `results/results.json`; the comparison and robustness summaries are in `results/comparison.md` and `results/robust.md`.
- The report describes the default configuration. If CLI parameters change, rerun the pipeline and revise this narrative against the new `results/results.json`.

## Appendix B. Viva preparation

| Question | Short answer |
|---|---|
| Why does relabelling not change uniqueness? | It changes node labels only. The graph is isomorphic, so each node keeps its degree and triangle count. |
| Why use degree and triangles? | They are simple local structural features that can be observed from a graph, but they are only a weak two-number signature. |
| What does `nx.triangles` return? | A mapping from each node to the number of triangles containing that node. |
| Why shuffle identifiers? | A seeded random bijection avoids making IDs correlate with generation order. |
| Why draw added edges from original non-edges? | It ensures additions were genuinely absent before perturbation and prevents a removed edge from being re-added. |
| Does rewiring preserve degrees? | No. It preserves the total number of edges, not each node's degree. |
| Why can clustering change? | Removing edges can break existing triangles, while random additions may not close new triangles. |
| Is a unique signature a privacy breach? | No. It is a potential risk indicator; it does not identify a real person. |
| Is this perturbation a proven defense? | No. It has no formal privacy guarantee or attacker analysis. |
| Would another generator change results? | It may; this report analyzes one base graph from one generator and does not claim model-independent findings. |
| How is a rank-five tie handled? | Ranking is deterministic by descending degree then identifier, and a tie at the fifth-place boundary is reported. |
| How is reproducibility ensured? | Separate stage seeds, sorted sampling inputs, recorded package versions, and repeated-run tests. |

## Appendix C. Filled results template (SRS Appendix E)

All values below come from `results/results.json` for the default seed-42 run. Display values use four decimal places; full precision remains in the JSON.

**Network.** Model: `powerlaw_cluster` (Holme–Kim); N = 100; m = 290; average degree = 5.8000; components = 1; total triangles = 152; average clustering = 0.3599.

**Relabelling check**

| | Unique count | Unique fraction |
|---|---:|---:|
| Named | 25 | 0.2500 |
| Anonymised | 25 | 0.2500 |
| Changed? | No (difference 0) | No (difference 0.0000) |

**Perturbation.** m = 290; k = 29, using `int(0.10 × 290 + 0.5)` (round half up). Seeds: master 42, names 43, anonymisation 44, primary perturbation 45.

**Comparison (anonymised vs perturbed)**

| Metric | Before | After | Change |
|---|---:|---:|---:|
| Unique count | 25 | 24 | -1 |
| Unique fraction | 0.2500 | 0.2400 | -0.0100 (-1 percentage point) |
| Average clustering | 0.3599 | 0.2805 | -0.0794 (-22.0562%) |
| Transitivity | 0.1806 | 0.1533 | -0.0273 |
| Components | 1 | 1 | 0 |
| Distinct signatures | 40 | 40 | 0 |
| Largest signature class | 18 | 15 | -3 |
| Originally unique nodes with unchanged signature | N/A | 3/25 (0.1200) | N/A |
| Originally unique nodes still unique | N/A | 17/25 (0.6800) | N/A |

**Top five by degree**

| Rank | Before (id, degree) | After (id, degree) |
|---:|---|---|
| 1 | U051, 33 | U051, 30 |
| 2 | U079, 23 | U055, 20 |
| 3 | U055, 20 | U079, 19 |
| 4 | U050, 17 | U050, 17 |
| 5 | U089, 17 | U089, 15 |

Overlap: 5 / 5. Same order: No. Tie at rank 5: No before, No after.

**Robustness (R = 200)**

| Metric | Mean | SD | Min | 5th pct | 95th pct | Max |
|---|---:|---:|---:|---:|---:|---:|
| Unique fraction after | 0.2322 | 0.0303 | 0.1200 | 0.1800 | 0.2800 | 0.3000 |
| Average clustering after | 0.2681 | 0.0178 | 0.2072 | 0.2400 | 0.2965 | 0.3160 |
| Top-five overlap | 4.3300 | 0.5487 | 3 | 4.0000 | 5.0000 | 5 |

**Interpretation statement (copied into Section 5).** The distinctive structural signatures observed illustrate a potential privacy concern. They do not establish that any person can actually be identified, because identification would additionally require accurate auxiliary knowledge, a reliable matching procedure, and a link from an anonymous node to a real individual.
