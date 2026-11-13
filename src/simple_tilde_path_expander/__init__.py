"""Public API for simple-tilde-path-expander.

Re-exports the two functions that make up the library's surface so callers
can write ``from simple_tilde_path_expander import expand_tilde, expand_tilde_path``
without reaching into the core module.
"""

from .core import expand_tilde, expand_tilde_path

__all__ = ["expand_tilde", "expand_tilde_path"]
