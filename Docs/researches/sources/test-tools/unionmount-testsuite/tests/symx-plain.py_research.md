# sources/test-tools/unionmount-testsuite/tests/symx-plain.py

Purpose: verifies plain opens through a dangling symlink without create fail with `ENOENT`.

Important APIs and functions: five subtests call `ctx.open_file()` on `ctx.pointless()` with read-only, write-only, append, read/write, and append read/write modes.

Control flow: each subtest constructs the broken symlink and absent target, then expects `ENOENT` for the open.

State and persistence: no file is created and no target data is modified because all operations fail.

Dependencies and integration: depends on harness broken-symlink fixtures and errno validation.

Risks: no postcondition checks are performed beyond open failure; if a buggy filesystem creates a target and still reports failure, this test alone would not detect the leftover.

Test signals: consistent `ENOENT` for every non-create open mode through the dangling symlink.
