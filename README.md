# Maskless

This project studies whether replacing names with anonymous identifiers hides structural patterns in a synthetic social network. It uses each node's degree and triangle count as a simple structural signature.

## Environment

The project has been developed on Arch Linux with system Python; a virtual environment is not required for this setup. Install the packages with `paru`:

```bash
paru -S python python-networkx python-pytest
```

Matplotlib is optional and is only needed for figures:

```bash
paru -S python-matplotlib
```

The pinned `requirements*.txt` files document package versions for portable pip-based installations, with version markers for Python 3.9 compatibility.

## Current workflow

Generate the default 100-node synthetic network, baseline statistics, structural-signature uniqueness, one perturbation comparison, and the default 200-run fixed-base robustness analysis:

```bash
python -m src.main --n 100 --model powerlaw_cluster --m 3 --p 0.5 \
  --seed 42 --rewire 0.10 --topk 5 --robust-runs 200 --out results
```

Override configuration, for example:

```bash
python -m src.main --n 50 --seed 7 --out results
```

The default model is `powerlaw_cluster`; `--model barabasi_albert` selects the supported alternative. The `--p` option is used by `powerlaw_cluster` as its triad-formation probability and does not affect the Barabási-Albert model.

Generated baseline and uniqueness summaries, the anonymous edge list, relabelling verification, perturbation edge lists, comparison JSON/Markdown/CSV, `results.json`, `robust.json`, `robust.md`, and optional figures are written to `results/`. The robustness analysis holds the anonymized base graph fixed and uses seeds `master seed + 1000 + i`; it reports mean, population standard deviation, minimum, 5th/95th percentiles (linear interpolation), and maximum for post-perturbation unique fraction, average clustering, and top-k overlap. Set `--robust-runs` to change the number of runs. The written results and interpretation are in [`report/report.md`](report/report.md); it describes the default seed-42 run, so revise it if you use different CLI settings. Replacing names with IDs changes labels, not topology, so the signature uniqueness count should remain exactly the same. The perturbation preserves edge count but may change degrees, triangles, clustering and connectedness. The named edge list and name-to-ID mapping are written to the ignored `private/` directory and must not be shared. Add `--no-plots` to skip optional figures. Run tests with:

```bash
pytest
```

## Scope and privacy

All network data is generated synthetically, and all names are fictional. No real person is targeted, no real personal data is used, and this project does not implement a re-identification attack or formal privacy mechanism. The wireless-social-network setting is motivational only; no radio or mobility simulation is performed.

> The distinctive structural signatures observed illustrate a potential privacy concern. They do not establish that any person can actually be identified, because identification would additionally require accurate auxiliary knowledge, a reliable matching procedure, and a link from an anonymous node to a real individual.
