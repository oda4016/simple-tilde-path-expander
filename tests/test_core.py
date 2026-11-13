import os
import unittest

from simple_tilde_path_expander import expand_tilde, expand_tilde_path


class ExpandTildeTests(unittest.TestCase):
    def test_plain_path_is_untouched(self):
        self.assertEqual(expand_tilde("/var/log/syslog"), "/var/log/syslog")

    def test_empty_string_is_returned(self):
        self.assertEqual(expand_tilde(""), "")

    def test_bare_tilde_uses_home(self):
        self.assertEqual(expand_tilde("~", home="/home/me"), "/home/me")

    def test_tilde_slash_uses_home(self):
        self.assertEqual(expand_tilde("~/docs", home="/home/me"), "/home/me/docs")

    def test_tilde_user_uses_that_users_home(self):
        # Without an explicit home we fall back to os.path.expanduser, which
        # is exactly what we want to verify here: the username is preserved.
        expected = os.path.expanduser("~alice") + "/notes"
        self.assertEqual(expand_tilde("~alice/notes"), expected)

    def test_explicit_home_overrides_username(self):
        self.assertEqual(
            expand_tilde("~alice/notes", home="/srv/alice"),
            "/srv/alice/notes",
        )

    def test_tilde_not_at_start_is_literal(self):
        self.assertEqual(expand_tilde("/a/~b"), "/a/~b")

    def test_tilde_followed_by_non_separator_non_user_is_literal(self):
        # ``~!`` is not a user name and not a separator; leave it alone.
        self.assertEqual(expand_tilde("~!/x"), "~!/x")

    def test_does_not_collapse_separators(self):
        self.assertEqual(expand_tilde("~/a//b", home="/h"), "/h/a//b")


class ExpandTildePathTests(unittest.TestCase):
    def test_collapses_redundant_separators(self):
        self.assertEqual(expand_tilde_path("/a//b///c"), "/a/b/c")

    def test_resolves_dot_and_dotdot(self):
        self.assertEqual(expand_tilde_path("/a/./b/../c"), "/a/c")

    def test_dotdot_at_root_stays_at_root(self):
        self.assertEqual(expand_tilde_path("/../a"), "/a")

    def test_relative_path_is_normalised_but_not_absolutised(self):
        self.assertEqual(expand_tilde_path("a/../b"), "b")

    def test_trailing_slash_is_dropped(self):
        self.assertEqual(expand_tilde_path("/a/b/"), "/a/b")

    def test_root_slash_is_preserved(self):
        self.assertEqual(expand_tilde_path("/"), "/")

    def test_leading_double_slash_is_preserved(self):
        # POSIX gives ``//`` implementation-defined meaning; normpath keeps it.
        self.assertEqual(expand_tilde_path("//a/b"), "//a/b")

    def test_tilde_expansion_happens_before_normalisation(self):
        self.assertEqual(
            expand_tilde_path("~/a/../b", home="/home/me"),
            "/home/me/b",
        )

    def test_empty_string_stays_empty(self):
        self.assertEqual(expand_tilde_path(""), "")

    def test_dotdot_above_relative_root_is_kept(self):
        # posixpath.normpath keeps leading ``..`` for relative paths; we do
        # not invent an absolute base for them.
        self.assertEqual(expand_tilde_path("../a"), "../a")

    def test_username_tilde_is_normalised_too(self):
        expected = os.path.expanduser("~alice") + "/b"
        self.assertEqual(expand_tilde_path("~alice/a/../b"), expected)


if __name__ == "__main__":
    unittest.main()
