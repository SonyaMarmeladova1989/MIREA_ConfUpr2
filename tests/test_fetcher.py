"""Tests for the fetcher module."""

from src.fetcher import _extract_requirement_name


def test_extract_requirement_name_simple():
    """The bare name should be returned unchanged."""
    assert _extract_requirement_name("requests") == "requests"


def test_extract_requirement_name_with_version():
    """Version specifiers should be stripped."""
    assert _extract_requirement_name("requests>=2.0") == "requests"


def test_extract_requirement_name_with_extras():
    """Extras in brackets should be stripped."""
    assert _extract_requirement_name("requests[security]") == "requests"


def test_extract_requirement_name_with_marker():
    """Environment markers should be stripped."""
    sample = 'requests; python_version >= "3.8"'
    assert _extract_requirement_name(sample) == "requests"
