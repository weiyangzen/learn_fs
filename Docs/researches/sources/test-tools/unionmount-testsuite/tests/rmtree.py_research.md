# sources/test-tools/unionmount-testsuite/tests/rmtree.py

Purpose: verifies recursive removal of a populated lower directory containing lower files.

Important APIs and functions: single `subtest_1(ctx)` uses `ctx.non_empty_dir()` and `ctx.rmtree()`.

Control flow: resolves a populated directory path, appends the harness trailing slash convention, and asks the context to recursively delete it.

State and persistence: removes a merged lower directory tree through the union mount, causing whiteouts or opaque state depending on implementation.

Dependencies and integration: depends entirely on the test harness `rmtree` helper for traversal and operation ordering.

Risks: no explicit post-removal opens are performed here, so failures are detected by exceptions from `rmtree` rather than later visibility checks.

Test signals: success is completion of recursive removal without unexpected errno.
