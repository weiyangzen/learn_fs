# sources/test-tools/unionmount-testsuite/tests/rename-new-dir.py

Purpose: tests rename behavior for empty directories created during the test. It covers round trips, deletion interactions, self-renames, replacements, and renaming over removed lower directories.

Important APIs and functions: contains fourteen `subtest_*` definitions, though the final four reuse names `subtest_11` and `subtest_12`; in normal Python import the later definitions shadow the earlier same-named functions. Uses `ctx.mkdir()`, `ctx.rename()`, `ctx.rmdir()`, `ctx.unlink()`, `ctx.open_dir()`, and `ctx.open_file()`.

Control flow: the active definitions include initial rename-back and remove/unlink checks, double rename, invalid replacement over populated dirs/files/parent, and cases where a new empty dir replaces an emptied or recursively removed lower dir.

State and persistence: the test creates upper-layer directories and validates that deleted lower names stay hidden or can be replaced. No file data is persisted except checks for absent lower children after replacement.

Dependencies and integration: depends on the harness collecting subtests by function name after module import. Duplicate function names are an integration risk because earlier cases can be silently lost.

Risks: duplicate `subtest_11` and `subtest_12` definitions likely reduce coverage. Replacement over lower directories is sensitive to opaque directory and whiteout semantics.

Test signals: expected `ENOENT`, `EISDIR`, `ENOTDIR`, or `ENOTEMPTY` results plus successful opens of final directory names.
