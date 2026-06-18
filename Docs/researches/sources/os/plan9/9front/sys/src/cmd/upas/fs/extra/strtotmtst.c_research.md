# File Research: sources/os/plan9/9front/sys/src/cmd/upas/fs/extra/strtotmtst.c

This test command includes `strtotm.c` directly and prints parsed dates.

Key behavior:
- Installs time formatting.
- For each argument, calls `strtotm`.
- Prints normalized formatted time on success or `bad` on failure.

Integration and risks:
- Direct include means it tests the exact parser implementation.
