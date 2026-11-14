"""Tests for the dependency graph builder."""

from src import constants
from src.config import Config
from src.graph import build_graph, build_reverse_graph

SAMPLE = """A: B, C
B: D
C: D, E
D:
E: A
"""


def _write_sample(tmp_path):
    path = tmp_path / "repo.txt"
    path.write_text(SAMPLE, encoding="utf-8")
    return str(path)


def _config(path, package="A", max_depth=10):
    return Config(
        package=package,
        repo_url=path,
        mode=constants.MODE_TEST,
        ascii_tree=False,
        max_depth=max_depth,
    )


def test_build_graph_marks_cycle(tmp_path):
    """Cyclic dependencies should be flagged but not recurse."""
    path = _write_sample(tmp_path)
    tree = build_graph(_config(path))
    assert tree["name"] == "A"
    b_node = [c for c in tree["children"] if c["name"] == "B"][0]
    assert b_node["children"][0]["name"] == "D"
    c_node = [c for c in tree["children"] if c["name"] == "C"][0]
    assert c_node["children"][1]["name"] == "E"


def test_build_graph_respects_depth(tmp_path):
    """Depth=1 must not recurse beyond direct children."""
    path = _write_sample(tmp_path)
    tree = build_graph(_config(path, max_depth=1))
    for child in tree["children"]:
        assert child["children"] == []


def test_build_reverse_graph(tmp_path):
    """Reverse graph must list dependents of each package."""
    path = _write_sample(tmp_path)
    reverse = build_reverse_graph(_config(path))
    assert "A" in reverse["E"]
    assert "B" in reverse["D"]
