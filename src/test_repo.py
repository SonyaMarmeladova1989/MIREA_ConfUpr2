"""Loader for the local test repository format."""

import re

from src.errors import FetchError

LINE_PATTERN = re.compile(r"^([A-Z]+)\s*:\s*(.*)$")


def parse_test_repository(path):
    """Parse a test repository file into a mapping."""
    graph = {}
    try:
        with open(path, encoding="utf-8") as handle:
            lines = handle.readlines()
    except (OSError, UnicodeError) as exc:
        raise FetchError(f"Cannot read test repository {path}: {exc}") from exc
    for raw in lines:
        line = raw.strip()
        if not line or line.startswith("#"):
            continue
        match = LINE_PATTERN.match(line)
        if not match:
            raise FetchError(f"Malformed test repository line: {line!r}")
        package = match.group(1)
        targets = [
            item.strip()
            for item in match.group(2).split(",")
            if item.strip()
        ]
        if any(not re.fullmatch(r"[A-Z]+", target) for target in targets):
            raise FetchError(f"Invalid dependency name in line: {line!r}")
        graph[package] = targets
    return graph
