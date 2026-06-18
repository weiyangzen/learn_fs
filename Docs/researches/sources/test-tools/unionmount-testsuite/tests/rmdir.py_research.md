# sources/test-tools/unionmount-testsuite/tests/rmdir.py

Purpose: validates `rmdir` behavior over nonexistent paths, files, empty lower dirs, populated dirs, copied-up contents, symlinks, dangling symlinks, and opaque recreated dirs.

Important APIs and functions: sixteen `subtest_*` functions call `ctx.rmdir()`, `ctx.rmtree()`, `ctx.unlink()`, `ctx.mkdir()`, `ctx.open_file()`, and fixture providers for files, dirs, direct/indirect symlinks, and broken symlinks.

Control flow: the test starts with negative nonexistent/file cases, proceeds through empty and populated directory removal sequences, mutates lower-populated dirs by unlinking/copying-up/recreating children, then checks directory symlink behavior and opaque directory recreation.

State and persistence: it creates and removes upper entries, whiteouts lower names, and verifies child file visibility after directory tree removal. Recreated directories test opacity after a lower directory was removed.

Dependencies and integration: relies on harness recursive removal and trailing slash behavior. It exercises overlayfs whiteout, opaque directory, and symlink traversal rules.

Risks: exact errno values for symlink plus trailing slash paths can be filesystem-specific. Recursive cleanup must be reliable or later assertions may see stale children.

Test signals: expected errno values, successful removal after children are deleted, and absent child files after `rmtree`.
