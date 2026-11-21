"""Tests for the fetcher module."""

import pytest

from src.errors import FetchError
from src.fetcher import _extract_requirement_name
from src.fetcher import fetch_direct_dependencies


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


@pytest.mark.parametrize("requirement", [" requests>=2", "requests\t>=2", "requests@https://example.org/pkg.whl"])
def test_extract_requirement_name_whitespace_and_direct_urls(requirement):
    assert _extract_requirement_name(requirement) == "requests"


@pytest.mark.parametrize("base, expected", [
    ("https://example.org", "https://example.org/pypi/requests/json"),
    ("https://example.org/api/", "https://example.org/api/requests/json"),
])
def test_fetch_uses_configured_repository(monkeypatch, base, expected):
    urls = []

    def get_json(url):
        urls.append(url)
        return {"info": {"requires_dist": ["urllib3>=1", "urllib3<3", "certifi"]}}

    monkeypatch.setattr("src.fetcher._http_get_json", get_json)
    assert fetch_direct_dependencies("requests", base) == ["urllib3", "certifi"]
    assert urls == [expected]


@pytest.mark.parametrize("metadata", [[], {}, {"info": []}, {"info": {"requires_dist": "requests"}},
                                       {"info": {"requires_dist": [42]}}])
def test_invalid_metadata_is_a_fetch_error(monkeypatch, metadata):
    monkeypatch.setattr("src.fetcher._http_get_json", lambda url: metadata)
    with pytest.raises(FetchError, match="metadata"):
        fetch_direct_dependencies("requests")
