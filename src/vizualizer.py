"""Render dependency graphs as ASCII trees and Mermaid."""

from src import constants


def _render_children(children, prefix, lines):
    """Recursively append tree lines for a children list."""
    last_position = len(children) - 1
    for index, child in enumerate(children):
        is_last = index == last_position
        connector = (
            constants.ASCII_LAST if is_last
            else constants.ASCII_BRANCH
        )
        marker = " (cycle)" if child.get("cycle") else ""
        lines.append(f"{prefix}{connector}{child['name']}{marker}")
        extension = " " * constants.ASCII_INDENT_WIDTH
        if not is_last:
            extension = "|" + extension[1:]
        _render_children(
            child.get("children", []), prefix + extension, lines
        )


def render_ascii_tree(tree):
    """Render the dependency tree as an ASCII-art string."""
    lines = [tree["name"]]
    _render_children(tree.get("children", []), "", lines)
    return "\n".join(lines)


def _collect_edges(tree):
    """Flatten a tree structure into an adjacency map."""
    result = {}
    stack = [tree]
    while stack:
        node = stack.pop()
        name = node["name"]
        if name in result:
            continue
        children = node.get("children", [])
        result[name] = [child["name"] for child in children]
        stack.extend(children)
    return result


def render_mermaid(tree):
    """Render the dependency graph in Mermaid syntax."""
    edges = _collect_edges(tree)
    lines = ["graph TD"]
    indent = constants.MERMAID_INDENT
    for source, targets in edges.items():
        if not targets:
            lines.append(f"{indent}{source}")
            continue
        for target in targets:
            lines.append(f"{indent}{source} --> {target}")
    return "\n".join(lines)
