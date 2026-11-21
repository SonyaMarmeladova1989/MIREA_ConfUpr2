"""Recursive DFS-based dependency graph construction."""

from src import constants
from src.fetcher import fetch_direct_dependencies
from src.errors import GraphError
from src.test_repo import parse_test_repository


def _load_repository(config):
    """Return an in-memory dependency map for test mode."""
    if config.mode == constants.MODE_TEST:
        repository = parse_test_repository(config.repo_url)
        if config.package not in repository:
            raise GraphError(f"Package not found in test repository: {config.package}")
        return repository
    return None


def _dependencies_of(package, repository, repo_url):
    """Return direct dependencies for a single package."""
    if repository is not None:
        return list(repository.get(package, []))
    return fetch_direct_dependencies(package, repo_url)


def build_graph(config):
    """Build the dependency tree via recursive DFS."""
    repository = _load_repository(config)
    dependencies = {}
    visiting = set()

    def visit(node, depth):
        node_tree = {"name": node, "children": []}
        if node in visiting:
            node_tree["cycle"] = True
            return node_tree
        if depth >= config.max_depth:
            return node_tree
        if node not in dependencies:
            dependencies[node] = _dependencies_of(node, repository, config.repo_url)
        visiting.add(node)
        node_tree["children"] = [
            visit(child, depth + constants.DEPTH_STEP)
            for child in dependencies[node]
        ]
        visiting.remove(node)
        return node_tree

    return visit(config.package, constants.INITIAL_DEPTH)


def _build_forward_map(config, repository):
    """Collect all edges as a name -> [targets] map via DFS."""
    edges = {}
    depths = {}

    def visit(node, depth):
        if node in depths and depths[node] <= depth:
            return
        depths[node] = depth
        if depth >= config.max_depth:
            edges.setdefault(node, [])
            return
        if node not in edges or not edges[node]:
            edges[node] = _dependencies_of(node, repository, config.repo_url)
        for child in edges[node]:
            visit(child, depth + constants.DEPTH_STEP)

    visit(config.package, constants.INITIAL_DEPTH)
    return edges


def build_reverse_graph(config):
    """Return reverse dependencies (who depends on the package)."""
    repository = _load_repository(config)
    forward = repository if repository is not None else _build_forward_map(config, repository)
    reverse = {config.package: []}
    for source, targets in forward.items():
        reverse.setdefault(source, [])
        for target in targets:
            reverse.setdefault(target, []).append(source)
    return reverse

