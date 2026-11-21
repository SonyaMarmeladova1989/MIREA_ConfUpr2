"""Application-wide constants."""

DEFAULT_MAX_DEPTH = 5
MIN_DEPTH = 1
MAX_DEPTH = 100
INITIAL_DEPTH = 0
DEPTH_STEP = 1

DEFAULT_REPO_URL = "https://pypi.org/pypi"
PYPI_JSON_URL = "{repo_url}/{package}/json"
HTTP_TIMEOUT_SECONDS = 10

MODE_REAL = "real"
MODE_TEST = "test"
VALID_MODES = (MODE_REAL, MODE_TEST)

ASCII_BRANCH = "├── "
ASCII_LAST = "└── "
ASCII_INDENT_WIDTH = 4
MERMAID_INDENT = "    "

