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

Generate the default 100-node synthetic network, baseline statistics and structural-signature uniqueness:

```bash
python -m src.main
```

Override configuration, for example:

```bash
python -m src.main --n 50 --seed 7 --out results
```

The default model is `powerlaw_cluster`; `--model barabasi_albert` selects the supported alternative. The `--p` option is used by `powerlaw_cluster` as its triad-formation probability and does not affect the Barabási-Albert model.

Generated baseline and uniqueness summaries, the anonymous edge list, and relabelling verification are written to `results/`. Replacing names with IDs changes labels, not topology, so the signature uniqueness count should remain exactly the same. The named edge list and name-to-ID mapping are written to the ignored `private/` directory and must not be shared. Run tests with:

```bash
pytest
```

## Scope and privacy

All network data is generated synthetically, and all names are fictional. No real person is targeted, no real personal data is used, and this project does not implement a re-identification attack or formal privacy mechanism. The wireless-social-network setting is motivational only; no radio or mobility simulation is performed. Structural distinctiveness is a potential privacy concern, not proof that a person can be identified.
