"""Command-line argument parsing."""

import argparse

from src import constants


def build_parser():
    """Construct the CLI argument parser."""
    parser = argparse.ArgumentParser(
        prog="depviz",
        description="Visualize Python package dependencies.",
    )
    parser.add_argument(
        "--package", required=True,
        help="Package name to analyze.",
    )
    parser.add_argument(
        "--repo-url", required=True,
        help="PyPI URL or path to test repository file.",
    )
    parser.add_argument(
        "--mode", choices=constants.VALID_MODES,
        default=constants.MODE_REAL,
        help="Repository mode (real or test).",
    )
    parser.add_argument(
        "--ascii-tree", action="store_true",
        help="Render dependencies as an ASCII tree.",
    )
    parser.add_argument(
        "--max-depth", type=int,
        default=constants.DEFAULT_MAX_DEPTH,
        help="Maximum dependency analysis depth.",
    )
    parser.add_argument(
        "--reverse", action="store_true",
        help="Show reverse dependencies.",
    )
    parser.add_argument(
        "--mermaid", action="store_true",
        help="Print dependency graph in Mermaid format.",
    )
    return parser


def parse_args(argv=None):
    """Parse CLI arguments from argv (or sys.argv if None)."""
    return build_parser().parse_args(argv)
