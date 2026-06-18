# sources/test-tools/unionmount-testsuite/tests/rename-pop-dir.py

Purpose: tests rename behavior for existing populated lower directories. It validates preserving descendants, invalid replacements, and replacement over empty directories.

Important APIs and functions: eleven `subtest_*` functions use `ctx.non_empty_dir()`, `ctx.empty_dir()`, `ctx.no_dir()`, `ctx.rename()`, `ctx.rmdir()`, `ctx.unlink()`, `ctx.open_dir()`, and `ctx.open_file()`.

Control flow: cases rename a populated dir away and back, remove/unlink old names, try removing non-empty directories, perform double rename, replace an empty directory, self-rename, and reject replacement over files, child files, and parent directory.

State and persistence: persistent state is a lower directory with child `a` and sometimes nested `pop/b`. The test expects child files to remain attached after legal renames and old paths to be hidden.

Dependencies and integration: depends on overlay copy-up or redirect semantics for lower populated directories. Harness errno checking distinguishes `ENOTEMPTY`, `EISDIR`, `ENOTDIR`, and `EINVAL`.

Risks: different filesystems can disagree on exact errno for invalid directory-over-file cases; the test encodes Linux overlay expectations.

Test signals: child `a` remains readable after valid renames; invalid operations leave source trees intact; removed source paths report `ENOENT`.
