"""Fetch package dependencies from PyPI without pip."""

import json
import urllib.parse
import urllib.request

from src import constants
from src.errors import FetchError

NAME_BREAK_CHARS = " \t[<>=!~;(@"


def _http_get_json(url):
    """Perform HTTP GET and decode JSON."""
    try:
        with urllib.request.urlopen(
            url, timeout=constants.HTTP_TIMEOUT_SECONDS
        ) as response:
            payload = response.read()
    except OSError as exc:
        raise FetchError(f"Request failed: {url}: {exc}") from exc
    try:
        return json.loads(payload.decode("utf-8"))
    except ValueError as exc:
        raise FetchError(f"Invalid JSON from {url}") from exc


def _extract_requirement_name(requirement):
    """Return the bare package name from a PEP 508 requirement."""
    requirement = requirement.strip()
    for sep in NAME_BREAK_CHARS:
        if sep in requirement:
            requirement = requirement.split(sep, 1)[0]
    return requirement.strip()


def _get_requirements(data, url):
    """Validate PyPI metadata and return its requirement strings."""
    if not isinstance(data, dict) or not isinstance(data.get("info"), dict):
        raise FetchError(f"Invalid package metadata from {url}")
    info = data["info"]
    requires = info.get("requires_dist") or []
    if not isinstance(requires, list) or any(
        not isinstance(item, str) for item in requires
    ):
        raise FetchError(f"Invalid requirements metadata from {url}")
    return requires


def fetch_direct_dependencies(package, repo_url=constants.DEFAULT_REPO_URL):
    """Return the list of direct dependency names for a package."""
    base_url = repo_url.rstrip("/")
    if not urllib.parse.urlsplit(base_url).path:
        base_url += "/pypi"
    url = constants.PYPI_JSON_URL.format(
        repo_url=base_url, package=urllib.parse.quote(package, safe="")
    )
    requires = _get_requirements(_http_get_json(url), url)
    names = []
    for requirement in requires:
        name = _extract_requirement_name(requirement)
        if name and name not in names:
            names.append(name)
    return names
