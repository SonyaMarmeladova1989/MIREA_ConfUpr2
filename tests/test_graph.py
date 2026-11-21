"""Tests for the dependency graph builder."""

import pytest

from src import constants
from src.config import Config
from src.errors import GraphError
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
    cycle = c_node["children"][1]["children"][0]
    assert cycle == {"name": "A", "children": [], "cycle": True}


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
    assert "C" in reverse["E"]
    assert "B" in reverse["D"]


def test_shared_dependency_is_expanded_at_each_depth(tmp_path):
    path = tmp_path / "repo.txt"
    path.write_text("A: B, C\nB: X\nX: D\nC: D\nD: E\nE:\n", encoding="utf-8")
    tree = build_graph(_config(str(path), max_depth=3))
    deep_d = tree["children"][0]["children"][0]["children"][0]
    shallow_d = tree["children"][1]["children"][0]
    assert deep_d == {"name": "D", "children": []}
    assert shallow_d["children"] == [{"name": "E", "children": []}]


def test_shared_dependency_cycle_depends_on_current_path(tmp_path):
    path = tmp_path / "repo.txt"
    path.write_text("A: B, C\nB: C\nC: B\n", encoding="utf-8")
    tree = build_graph(_config(str(path)))
    b_cycle = tree["children"][0]["children"][0]["children"][0]
    c_cycle = tree["children"][1]["children"][0]["children"][0]
    assert b_cycle == {"name": "B", "children": [], "cycle": True}
    assert c_cycle == {"name": "C", "children": [], "cycle": True}


def test_reverse_includes_packages_outside_forward_graph(tmp_path):
    path = tmp_path / "repo.txt"
    path.write_text("A: B\nB:\nC: A\n", encoding="utf-8")
    assert build_reverse_graph(_config(str(path)))["A"] == ["C"]


def test_unknown_test_package_is_an_error(tmp_path):
    path = _write_sample(tmp_path)
    with pytest.raises(GraphError, match="Package not found"):
        build_graph(_config(path, package="UNKNOWN"))


def test_real_reverse_respects_depth_and_revisits_shorter_paths(monkeypatch):
    repository = {"A": ["B", "C"], "B": ["X"], "X": ["D"], "C": ["D"],
                  "D": ["E"], "E": ["F"], "F": []}
    calls = []

    def fetch(package, repo_url):
        calls.append((package, repo_url))
        return repository[package]

    monkeypatch.setattr("src.graph.fetch_direct_dependencies", fetch)
    config = _config("https://example.org/pypi", max_depth=3)
    config.mode = constants.MODE_REAL
    reverse = build_reverse_graph(config)
    assert reverse["E"] == ["D"]
    assert "F" not in reverse
    assert ("E", config.repo_url) not in calls
    assert all(url == config.repo_url for _, url in calls)
