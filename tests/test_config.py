import pytest

from src.config import Config, parse_config


def test_defaults_and_derived_seeds():
    config = parse_config([])
    assert config == Config()
    assert config.seeds == {
        "master": 42,
        "names": 43,
        "anon": 44,
        "perturb": 45,
        "robust_base": 1042,
    }


def test_cli_overrides():
    config = parse_config(
        ["--n", "50", "--m", "2", "--p", "0.2", "--seed", "7", "--out", "out"]
    )
    assert (config.n, config.m_attach, config.p_triad) == (50, 2, 0.2)
    assert config.master_seed == 7
    assert str(config.out_dir) == "out"


@pytest.mark.parametrize(
    "args",
    [
        ["--n", "2"],
        ["--rewire", "1.5"],
        ["--topk", "101"],
        ["--m", "100"],
        ["--m", "0"],
        ["--p", "-0.1"],
    ],
)
def test_invalid_cli_config_is_rejected(args):
    with pytest.raises(ValueError):
        parse_config(args)
