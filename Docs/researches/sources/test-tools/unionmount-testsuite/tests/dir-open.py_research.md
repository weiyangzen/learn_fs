# sources/test-tools/unionmount-testsuite/tests/dir-open.py

Purpose: tests opening existing populated directories without `O_DIRECTORY`.

Important APIs/types/functions: six `subtest_*` functions using `ctx.open_file`.

Control flow: read-only open of a directory is expected to succeed. Write-only, repeated write-only, append, read/write, and append/read-write variants expect `EISDIR`; each failed write-like operation is followed by successful read-only open.

State and persistence: should not mutate the directory tree or file contents.

Dependencies and integration: uses `ctx.non_empty_dir`, terminal-slash mode, and `open_file` error/layer checks.

Risks: some filesystems can differ on directory open permissions, but the suite encodes Linux VFS expectations.

Test signals: validates directory error behavior for non-`O_DIRECTORY` opens and post-failure stability.
