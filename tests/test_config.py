"""Tests for the configuration module."""

import pytest

from src import constants
from src.config import (
    build_config,
    validate_depth,
    validate_mode,
    validate_package,
    validate_repo_url,
)
from src.errors import ConfigError


class Args:
    """Minimal stand-in for parsed CLI arguments."""

    def __init__(self, **kwargs):
        self.__dict__.update(kwargs)


def _args(**overrides):
    defaults = {
        "package": "A",
        "repo_url": "path.txt",
        "mode": constants.MODE_TEST,
        "ascii_tree": False,
        "max_depth": constants.DEFAULT_MAX_DEPTH,
        "reverse": False,
        "mermaid": False,
    }
    defaults.update(overrides)
    return Args(**defaults)


def test_validate_package_rejects_empty():
    """Empty package names should raise a ConfigError."""
    with pytest.raises(ConfigError):
        validate_package(" \u00a0")


def test_validate_repo_url_rejects_empty():
    """Empty repository paths should raise a ConfigError."""
    with pytest.raises(ConfigError):
        validate_repo_url("")


def test_validate_mode_rejects_unknown():
    """Unsupported modes should raise a ConfigError."""
    with pytest.raises(ConfigError):
        validate_mode("staging")


def test_validate_depth_bounds():
    """Depth must stay inside the allowed range."""
    with pytest.raises(ConfigError):
        validate_depth(constants.MIN_DEPTH - 1)
    with pytest.raises(ConfigError):
        validate_depth(constants.MAX_DEPTH + 1)


def test_build_config_requires_existing_test_file(tmp_path):
    """Test mode should require an existing file."""
    missing = tmp_path / "missing.txt"
    with pytest.raises(ConfigError):
        build_config(_args(repo_url=str(missing)))


@pytest.mark.parametrize("url", [
    "file:///etc/passwd",
    "not-a-url",
    "https://[",
    "https://example.org?query=1",
])
def test_real_repository_must_be_an_http_api_url(url):
    with pytest.raises(ConfigError):
        build_config(_args(mode=constants.MODE_REAL, repo_url=url))
