"""Recursive DFS-based dependency graph construction."""

from src import constants
from src.fetcher import fetch_direct_dependencies
from src.test_repo import parse_test_repository

def _load_repository(config):
    """Return an in-memory dependency map for test mode."""
    if config.mode == constants.MODE_TEST:
        return parse_test_repository(config.repo_url)
    return None


def _dependencies_of(package, repository):
    """Return direct dependencies for a single package."""
    if repository is not None:
        return list(repository.get(package, []))
    return fetch_direct_dependencies(package)


def build_graph(config):
    """Build the dependency tree via recursive DFS."""
    repository = _load_repository(config)
    visited = {}
    visiting = set()

    def visit(node, depth):
        if depth > config.max_depth:
            return []
        if node in visiting:
            return [{"name": node, "children": [], "cycle": True}]
        if node in visited:
            return visited[node]
        visiting.add(node)
        children = []
        for child in _dependencies_of(node, repository):
            subtree = visit(child, depth + constants.DEPTH_STEP)
            children.append({"name": child, "children": subtree})
        visiting.discard(node)
        visited[node] = children
        return children

    children = visit(config.package, constants.INITIAL_DEPTH)
    return {"name": config.package, "children": children}


def _build_forward_map(config, repository):
    """Collect all edges as a name -> [targets] map via DFS."""
    edges = {}
    visiting = set()

    def visit(node, depth):
        if depth > config.max_depth or node in edges:
            return
        if node in visiting:
            return
        visiting.add(node)
        children = _dependencies_of(node, repository)
        edges[node] = children
        for child in children:
            visit(child, depth + constants.DEPTH_STEP)
        visiting.discard(node)

    visit(config.package, constants.INITIAL_DEPTH)
    return edges


def build_reverse_graph(config):
    """Return reverse dependencies (who depends on the package)."""
    repository = _load_repository(config)
    forward = _build_forward_map(config, repository)
    reverse = {config.package: []}
    for source, targets in forward.items():
        reverse.setdefault(source, [])
        for target in targets:
            reverse.setdefault(target, []).append(source)
    return reverse

