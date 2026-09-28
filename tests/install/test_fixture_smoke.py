"""Smoke test that the tmp_silas_home fixture works."""

from __future__ import annotations

from pathlib import Path

from silas.core import config as config_mod


def test_fixture_redirects_default_config_dir(tmp_silas_home: Path) -> None:
    assert config_mod.DEFAULT_CONFIG_DIR == tmp_silas_home
    assert tmp_silas_home.exists()
    assert (tmp_silas_home / ".state").exists()
    assert (tmp_silas_home / ".state" / "models").exists()


def test_fixture_redirects_config_path(tmp_silas_home: Path) -> None:
    assert config_mod.DEFAULT_CONFIG_PATH == tmp_silas_home / "config.toml"
