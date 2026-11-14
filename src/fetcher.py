"""Fetch package dependencies from PyPI without pip."""

import json
import urllib.request

from src import constants
from src.errors import FetchError

NAME_BREAK_CHARS = " [<>=!~;("


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
    for sep in NAME_BREAK_CHARS:
        if sep in requirement:
            requirement = requirement.split(sep, 1)[0]
    return requirement.strip()


def fetch_direct_dependencies(package):
    """Return the list of direct dependency names for a package."""
    url = constants.PYPI_JSON_URL.format(package=package)
    data = _http_get_json(url)
    info = data.get("info") or {}
    requires = info.get("requires_dist") or []
    names = []
    for requirement in requires:
        name = _extract_requirement_name(requirement)
        if name and name not in names:
            names.append(name)
    return names

