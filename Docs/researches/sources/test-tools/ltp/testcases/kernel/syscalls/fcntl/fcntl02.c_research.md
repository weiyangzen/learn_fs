# sources/test-tools/ltp/testcases/kernel/syscalls/fcntl/fcntl02.c

Purpose: basic `F_DUPFD` test verifying duplicated descriptors are at least the requested minimum fd.

Important APIs/types/functions: `fcntl(fd, F_DUPFD, min_fd)`, `SAFE_OPEN`, `SAFE_CLOSE`, `TEST`, `TST_RET`, and modern `struct tst_test`.

Control flow: setup opens a temp file. The test iterates minimum fd values `0, 1, 2, 3, 10, 100`, duplicates the open fd, checks success and returned value `>= min_fd`, then closes each duplicate.

State/persistence behavior: one original fd persists for the test; duplicate fds are transient descriptor-table state.

Dependencies/integration: tempdir and modern LTP API.

Risks/test signals: simple contract. Failure indicates `F_DUPFD` returned below the minimum or failed unexpectedly.
