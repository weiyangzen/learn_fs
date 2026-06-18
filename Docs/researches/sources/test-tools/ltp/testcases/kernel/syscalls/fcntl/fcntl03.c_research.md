# sources/test-tools/ltp/testcases/kernel/syscalls/fcntl/fcntl03.c

Purpose: basic `F_GETFD` test verifying descriptor flags can be queried on a valid fd.

Important APIs/types/functions: `fcntl(fd, F_GETFD, 0)`, `SAFE_OPEN`, `SAFE_CLOSE`, `TEST`, and `tst_res`.

Control flow: setup opens a temp file. The test calls `fcntl` and reports pass on any nonnegative return.

State/persistence behavior: one open file descriptor persists until cleanup. No descriptor flags are changed.

Dependencies/integration: modern LTP tempdir test.

Risks/test signals: minimal API liveness check. It does not assert an exact default flag value.
