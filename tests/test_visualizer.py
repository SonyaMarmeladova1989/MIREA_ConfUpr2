"""Tests for the ASCII and Mermaid renderers."""

from src.visualizer import render_ascii_tree, render_mermaid

TREE = {
    "name": "A",
    "children": [
        {"name": "B", "children": []},
        {"name": "C", "children": [
            {"name": "D", "children": [], "cycle": True},
        ]},
    ],
}


def test_render_ascii_tree_contains_packages():
    """Every package in the tree must appear in ASCII output."""
    output = render_ascii_tree(TREE)
    for name in ("A", "B", "C", "D"):
        assert name in output


def test_render_ascii_tree_marks_cycle():
    """Cycles should be annotated explicitly."""
    output = render_ascii_tree(TREE)
    assert "(cycle)" in output


def test_render_mermaid_contains_edges():
    """Mermaid output must contain the dependency edges."""
    output = render_mermaid(TREE)
    assert "graph TD" in output
    assert "A --> B" in output
    assert "C --> D" in output


def test_mermaid_keeps_edges_when_a_leaf_is_seen_first():
    tree = {"name": "A", "children": [
        {"name": "B", "children": [{"name": "D", "children": []}]},
        {"name": "B", "children": []},
    ]}
    output = render_mermaid(tree)
    assert "B --> D" in output
    assert output.count("A --> B") == 1
