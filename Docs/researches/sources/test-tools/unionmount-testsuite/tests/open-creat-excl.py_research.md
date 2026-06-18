# sources/test-tools/unionmount-testsuite/tests/open-creat-excl.py

Purpose: verifies `O_CREAT|O_EXCL` fails on existing lower files without changing them.

Important APIs/types/functions: five `subtest_*` functions using `ctx.open_file`.

Control flow: attempts read-only, write-only, append, read-write, and append/read-write exclusive opens, all expecting `EEXIST`, then reads original content.

State and persistence: no file content or layer state should change.

Dependencies and integration: context open flag handling and lower regular fixtures.

Risks: some paths with terminal slash can produce slash-related errors instead of `EEXIST`.

Test signals: baseline exclusive-open existing-file regression coverage.
