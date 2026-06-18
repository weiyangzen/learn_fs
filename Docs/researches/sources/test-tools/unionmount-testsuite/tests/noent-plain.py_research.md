# sources/test-tools/unionmount-testsuite/tests/noent-plain.py

Purpose: verifies opening absent files without create flags fails consistently.

Important APIs/types/functions: five `subtest_*` functions using `ctx.open_file`.

Control flow: read-only, write-only, append, read-write, and append/read-write opens are attempted twice against a missing path, each expecting `ENOENT`.

State and persistence: no intended mutation; missing dentry should remain absent after all attempts.

Dependencies and integration: depends on setup missing dentry records and context error handling.

Risks: terminal slash mode can alter missing path errors in some contexts, but expected result here is `ENOENT`.

Test signals: baseline negative-open behavior and failed-create state stability.
