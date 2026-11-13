import os
import posixpath
import re

__all__ = ["expand_tilde", "expand_tilde_path"]

# Matches a leading tilde followed by a username.  We deliberately do NOT
# treat ``~`` followed by a path separator as a username: ``~/foo`` is the
# current user's home, ``~bob/foo`` is bob's home.
_TILDE_USER_RE = re.compile(r"^~([^/\\]+)")


def expand_tilde(path, home=None):
    """Expand a leading tilde in *path* to a home directory.

    Only the *leading* tilde is considered.  A tilde elsewhere in the path is
    a literal character and is left alone.

    ``~`` and ``~/...`` expand to *home* when supplied, otherwise to
    ``os.path.expanduser("~")``.  ``~user`` and ``~user/...`` expand to the
    home of *user* when *home* is not supplied; if *home* is supplied it is
    used for any tilde form, which keeps the function pure and testable.

    The result is returned as a plain string.  No separator collapsing or
    parent resolution is performed here; use :func:`expand_tilde_path` for
    that.
    """
    if not path:
        return path

    if not path.startswith("~"):
        return path

    # ``~`` alone, or ``~/...``, or ``~\\...`` on Windows-style input.
    if len(path) == 1:
        return _home_for(None, home)
    if path[1] in ("/", "\\"):
        return _home_for(None, home) + path[1:]

    match = _TILDE_USER_RE.match(path)
    if match is None:
        # A tilde followed by something that is not a user name or separator
        # (for example ``~!``) is not a home reference; leave it untouched.
        return path

    user = match.group(1)
    rest = path[len(user) + 1:]
    return _home_for(user, home) + rest


def _home_for(user, home):
    """Return the home directory for *user*.

    When *home* is given it always wins.  This is the hook that makes the
    function deterministic in tests without touching the real environment.
    """
    if home is not None:
        return home
    if user is None:
        return os.path.expanduser("~")
    return os.path.expanduser("~" + user)


def expand_tilde_path(path, home=None):
    """Expand a leading tilde and normalise the resulting path.

    Normalisation collapses redundant separators, resolves ``.`` and ``..``
    components, and drops a trailing slash (except for the root).  It is
    lexical only: ``..`` is resolved against the preceding component even if
    that component is a symlink, because the function never touches the
    filesystem beyond the home lookup.  That is the deliberate trade-off:
    callers who need symlink-aware resolution should use
    ``os.path.realpath`` afterwards.

    A relative path with no tilde is normalised but not made absolute.
    """
    expanded = expand_tilde(path, home=home)
    return _normalise(expanded)


def _normalise(path):
    """Lexically normalise *path* using POSIX rules.

    We use :mod:`posixpath` rather than :mod:`os.path` so that behaviour is
    identical on every platform, including Windows where ``os.path`` would
    treat backslashes as separators.  Paths in this library are treated as
    POSIX-style strings.
    """
    if not path:
        return path

    # Preserve a leading double slash: POSIX allows it to have
    # implementation-defined meaning, and silently collapsing it would be
    # surprising.  posixpath.normpath already preserves exactly two leading
    # slashes, so we only need to guard the empty case above.
    return posixpath.normpath(path)
