"""Custom exceptions for the dependency analyzer."""


class ConfigError(Exception):
    """Raised when a configuration parameter is invalid."""


class FetchError(Exception):
    """Raised when dependency data cannot be retrieved."""


class GraphError(Exception):
    """Raised when the dependency graph cannot be built."""
