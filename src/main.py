"""Entry point orchestrating all stages of the analyzer."""

import sys

from src import cli
from src import config as config_module
from src.errors import ConfigError, FetchError, GraphError
from src.graph import build_graph, build_reverse_graph
from src.visualizer import render_ascii_tree, render_mermaid


def _print_config(config):
    """Print all user-configurable parameters."""
    print("== Configuration ==")
    for key, value in config_module.describe_config(config):
        print(f"{key}={value}")


def _handle_error(exc):
    """Print the error to stderr and return exit code 1."""
    print(f"error: {exc}", file=sys.stderr)
    return 1


def _render_reverse(config):
    """Print reverse dependencies of the target package."""
    reverse = build_reverse_graph(config)
    print("== Reverse dependencies ==")
    for name, dependents in reverse.items():
        joined = ", ".join(dependents) or "-"
        print(f"{name}: {joined}")


def main(argv=None):
    """Run the dependency analyzer end-to-end."""
    args = cli.parse_args(argv)
    try:
        config = config_module.build_config(args)
    except ConfigError as exc:
        return _handle_error(exc)

    _print_config(config)

    try:
        if config.reverse:
            _render_reverse(config)
            return 0
        tree = build_graph(config)
    except (FetchError, GraphError) as exc:
        return _handle_error(exc)

    if config.mermaid:
        print("== Mermaid ==")
        print(render_mermaid(tree))

    if config.ascii_tree:
        print("== ASCII tree ==")
        print(render_ascii_tree(tree))

    return 0


if __name__ == "__main__":
    sys.exit(main())
