# sources/test-tools/ltp/testcases/kernel/syscalls/faccessat/faccessat02.c

Purpose: Negative coverage for `faccessat()` with a non-directory dirfd and an invalid fd.

Important APIs/types/functions: `faccessat`, `TST_EXP_FAIL`, `ENOTDIR`, `EBADF`, `SAFE_MKDIR`, `SAFE_OPEN`, and a two-row testcase table.

Control flow: `setup()` creates the same directory/file layout as the positive test. One case passes the file fd with a relative name expecting `ENOTDIR`; the other passes `-1` expecting `EBADF`.

State and persistence behavior: The tmpdir file and fds are the only state. No access check should succeed.

Dependencies and integration points: Complements `faccessat01.c` and uses the same LTP tmpdir/fd cleanup pattern.

Risks and test signals: Kernel changes in dirfd validation would surface as wrong errno. The cases intentionally avoid absolute paths so dirfd validation is exercised.
