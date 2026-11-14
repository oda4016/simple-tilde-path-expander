# simple-tilde-path-expander

Expands a leading `~` in a path to a home directory and normalises the result
by collapsing redundant separators and resolving `.` and `..` components.

```python
from simple_tilde_path_expander import expand_tilde, expand_tilde_path

expand_tilde("~/notes")
# '/home/you/notes'

expand_tilde("~alice/notes")
# '/home/alice/notes'

expand_tilde("~/notes", home="/srv/you")
# '/srv/you/notes'

expand_tilde_path("~/a//b/../c")
# '/home/you/a/c'

expand_tilde_path("/a/./b/../c")
# '/a/c'
```

The two exported names are `expand_tilde` and `expand_tilde_path`. Both take
an optional `home` keyword argument. `expand_tilde` only rewrites the leading
tilde; `expand_tilde_path` additionally normalises the path.

## Why this exists

`os.path.expanduser` rewrites `~` but leaves `//`, `.` and `..` in place, and
`os.path.normpath` does the opposite. Chaining them is easy to get wrong
because the order matters: expanding after normalising can turn `~` into a
literal component, and normalising after expanding can walk out of the home
directory in ways the caller did not intend. This library does both steps in a
single documented order — expand first, then normalise — so the result is
predictable.

The trade-off is that normalisation is lexical. `..` is resolved against the
preceding path component as text, not against the filesystem. If `a/b` is a
symlink to `elsewhere/x`, then `a/b/..` becomes `a`, not `elsewhere`. That is
the same choice `os.path.normpath` makes, and it keeps the function pure and
fast. Callers who need symlink-aware resolution should pass the result through
`os.path.realpath` afterwards.

## The awkward edge

A tilde that is not at the start of the path is a literal character, and a
tilde followed by something that is neither a separator nor a plausible user
name (for example `~!`) is also left alone. So `expand_tilde("/a/~b")` returns
`"/a/~b"`, not a home directory. Only the leading tilde is special.
