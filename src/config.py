"""User-configurable settings parsing and validation."""

import os
from urllib.parse import urlsplit
from dataclasses import dataclass

from src import constants
from src.errors import ConfigError


@dataclass
class Config:
    """Container for all user-configurable parameters."""

    package: str
    repo_url: str
    mode: str
    ascii_tree: bool
    max_depth: int
    reverse: bool = False
    mermaid: bool = False


def validate_package(package):
    """Ensure the package name is a non-empty string."""
    if not package or not package.strip():
        raise ConfigError("Package name must not be empty.")
    return package.strip()


def validate_repo_url(url):
    """Ensure the repository URL or path is present."""
    if not url or not url.strip():
        raise ConfigError("Repository URL or path must not be empty.")
    return url.strip()


def validate_mode(mode):
    """Ensure the mode is one of the supported values."""
    if mode not in constants.VALID_MODES:
        raise ConfigError(
            f"Mode must be one of {constants.VALID_MODES}.")
    return mode


def validate_depth(depth):
    """Ensure the analysis depth is inside the allowed range."""
    if depth < constants.MIN_DEPTH:
        raise ConfigError(
            f"Max depth must be >= {constants.MIN_DEPTH}.")
    if depth > constants.MAX_DEPTH:
        raise ConfigError(
            f"Max depth must be <= {constants.MAX_DEPTH}.")
    return depth


def validate_test_path(path):
    """Ensure the test repository file actually exists."""
    if not os.path.isfile(path):
        raise ConfigError(f"Test repository file not found: {path}")
    return path


def build_config(args):
    """Validate CLI arguments and produce a Config instance."""
    package = validate_package(args.package)
    repo_url = validate_repo_url(args.repo_url)
    mode = validate_mode(args.mode)
    depth = validate_depth(args.max_depth)
    if mode == constants.MODE_TEST:
        validate_test_path(repo_url)
    else:
        try:
            url = urlsplit(repo_url)
        except ValueError as exc:
            raise ConfigError("Invalid repository URL.") from exc
        if (
            url.scheme not in ("http", "https")
            or not url.netloc
            or url.query
            or url.fragment
        ):
            raise ConfigError(
                "Repository URL must be an HTTP(S) JSON API base URL."
            )
    return Config(
        package=package,
        repo_url=repo_url,
        mode=mode,
        ascii_tree=args.ascii_tree,
        max_depth=depth,
        reverse=args.reverse,
        mermaid=args.mermaid,
    )


def describe_config(config):
    """Return the config as a list of key-value pairs."""
    return [
        ("package", config.package),
        ("repo_url", config.repo_url),
        ("mode", config.mode),
        ("ascii_tree", config.ascii_tree),
        ("max_depth", config.max_depth),
        ("reverse", config.reverse),
        ("mermaid", config.mermaid),
    ]
