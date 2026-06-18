# sources/test-tools/unionmount-testsuite/tests/sym1-creat-excl.py

Purpose: verifies that opening a direct symlink to an existing file with `O_CREAT|O_EXCL` fails with `EEXIST` and leaves the target unchanged.

Important APIs and functions: five subtests cover read-only, write-only, append write-only, read/write, and append read/write combinations through `ctx.open_file()`.

Control flow: each subtest builds a direct symlink path from `ctx.direct_sym()`, attempts an exclusive create expecting `EEXIST`, then reopens the symlink read-only and expects original content `:xxx:yyy:zzz`.

State and persistence: the test should not change file data. Persistence signal is that the lower target remains readable and unchanged after failed opens.

Dependencies and integration: depends on harness mapping flag booleans `ro`, `wo`, `rw`, `app`, `crt`, and `ex` into open flags.

Risks: one case passes `ro=1, app=1` for an append read/write label, mirroring surrounding tests but relying on harness interpretation.

Test signals: `EEXIST` on each exclusive create and unchanged file contents after each failure.
