# sources/test-tools/ltp/testcases/kernel/syscalls/fcntl/fcntl12.c

Purpose: verifies `F_DUPFD` fails with `EMFILE` when the process file descriptor table is exhausted.

Important APIs/types/functions: `getdtablesize`, `open`, `fcntl(F_DUPFD)`, `TST_EXP_FAIL2`, `SAFE_FORK`, and `tst_reap_children`.

Control flow: setup records the descriptor-table size. The test forks a child; the child opens the same file repeatedly until open fails, then calls `fcntl(1, F_DUPFD, 1)` and expects `EMFILE`. The parent reaps the child.

State/persistence behavior: descriptor exhaustion occurs only in the child and is released on child exit. The shared temp filename is unlinked in cleanup.

Dependencies/integration: modern LTP fork/tempdir test.

Risks/test signals: relies on being able to consume all fd slots. External rlimits or inherited descriptors affect the exact loop count but not the expected final errno.
