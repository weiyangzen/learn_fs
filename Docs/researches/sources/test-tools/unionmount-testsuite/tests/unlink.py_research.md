# sources/test-tools/unionmount-testsuite/tests/unlink.py

Purpose: validates unlink behavior for files, direct and indirect symlinks, directories, directory symlinks, absent files, and broken symlinks.

Important APIs and functions: ten `subtest_*` functions use `ctx.unlink()`, `ctx.open_file()`, `ctx.open_dir()`, and fixture helpers for regular files, symlinks, directory symlinks, and broken symlinks.

Control flow: file and symlink cases unlink an object, verify it disappears, and verify targets remain where relevant. Directory cases expect `EISDIR`. Directory symlink cases account for trailing-slash mode, where path resolution may still open the target after unlink. Absent and broken symlink cases assert `ENOENT` on repeat unlink.

State and persistence: unlink creates whiteouts for lower names or removes upper symlinks. Target files/directories should persist when only symlink dentries are removed.

Dependencies and integration: depends on context trailing slash behavior and fixture isolation.

Risks: subtests 8 and 9 are effectively identical dangling-symlink unlink checks. Trailing slash semantics around symlinks are a known portability hazard.

Test signals: expected `EISDIR` or `ENOENT`, target preservation after symlink unlink, and removed path invisibility.
