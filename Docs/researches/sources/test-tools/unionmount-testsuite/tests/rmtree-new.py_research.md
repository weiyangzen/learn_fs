# sources/test-tools/unionmount-testsuite/tests/rmtree-new.py

Purpose: tests recursive removal of a lower populated directory after adding a new upper subdirectory inside it.

Important APIs and functions: one `subtest_1(ctx)` uses `ctx.non_empty_dir()`, `ctx.mkdir()`, and `ctx.rmtree()`.

Control flow: it selects a populated directory, creates a new child `b`, then recursively removes the parent directory.

State and persistence: state spans merged lower contents and newly created upper contents. The important behavior is that recursive removal handles both layers as one merged tree.

Dependencies and integration: depends on the harness `rmtree` helper to issue the correct unlink/rmdir sequence through the union mount.

Risks: minimal assertions after removal mean this primarily detects syscall failure, not every possible leftover hidden entry.

Test signals: the recursive remove operation completes without unexpected errors.
