import json

import pytest

from src.config import Config
from src.main import _execute_pipeline, _write_shareable_outputs, main


def test_results_json_contains_srs_data_dictionary_and_is_sorted(tmp_path):
    config = Config(
        n=30,
        m_attach=2,
        master_seed=9,
        top_k=3,
        robust_runs=2,
        out_dir=tmp_path,
        no_plots=True,
    )
    result = _execute_pipeline(config)
    timestamp = "2026-01-01T00:00:00+00:00"

    _write_shareable_outputs(config, result, timestamp)
    first_outputs = {
        path.relative_to(tmp_path): path.read_bytes()
        for path in tmp_path.rglob("*")
        if path.is_file()
    }
    _write_shareable_outputs(config, _execute_pipeline(config), timestamp)
    assert first_outputs == {
        path.relative_to(tmp_path): path.read_bytes()
        for path in tmp_path.rglob("*")
        if path.is_file()
    }

    path = tmp_path / "results.json"
    text = path.read_text(encoding="utf-8")
    payload = json.loads(text)
    assert list(payload) == sorted(payload)
    assert text.endswith("\n")
    assert payload["meta"]["timestamp"] == timestamp
    assert set(payload["meta"]["seeds"]) == {"master", "names", "anon", "perturb"}
    assert {"n", "m", "density", "degree_min", "degree_mean", "degree_max",
            "components", "total_triangles", "transitivity", "avg_clustering"} <= set(
                payload["baseline"]
            )
    assert set(payload["named"]) == {"unique_count", "unique_fraction"}
    assert set(payload["anon"]) == {"unique_count", "unique_fraction"}
    assert set(payload["relabel"]) == {
        "fraction_changed",
        "per_node_match",
        "edges_match",
        "isomorphic",
    }
    assert {"m", "k", "removed", "added"} <= set(payload["perturb"])
    assert payload["compare"]["top5_before"] is None
    assert payload["compare"]["top_k"] == 3
    assert payload["robust"]["runs"] == 2


@pytest.mark.parametrize("args", [["--n", "2"], ["--rewire", "1.5"]])
def test_cli_validation_returns_exit_code_one(args, capsys):
    assert main(args) == 1
    assert "error:" in capsys.readouterr().err
