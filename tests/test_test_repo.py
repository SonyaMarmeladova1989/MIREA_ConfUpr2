"""Tests for the test repository parser."""

import pytest

from src.errors import FetchError
from src.test_repo import parse_test_repository

SAMPLE = """# comment
A: B, C
B: D
C: D, E
D:
E: A
"""


def test_parse_valid_file(tmp_path):
    """Valid files should produce the expected mapping."""
    path = tmp_path / "repo.txt"
    path.write_text(SAMPLE, encoding="utf-8")
    graph = parse_test_repository(str(path))
    assert graph["A"] == ["B", "C"]
    assert graph["B"] == ["D"]
    assert graph["D"] == []


def test_parse_malformed_line(tmp_path):
    """Malformed lines should raise FetchError."""
    path = tmp_path / "repo.txt"
    path.write_text("not a valid line\n", encoding="utf-8")
    with pytest.raises(FetchError):
        parse_test_repository(str(path))
