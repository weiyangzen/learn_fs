# sources/test-tools/ltp/testcases/kernel/syscalls/faccessat/faccessat01.c

Purpose: Positive coverage for `faccessat()` path resolution with directory fd, absolute path, and `AT_FDCWD`.

Important APIs/types/functions: `faccessat`, `TST_EXP_PASS`, `tst_tmpdir_genpath`, `SAFE_MKDIR`, `SAFE_OPEN(... O_DIRECTORY)`, `AT_FDCWD`, and LTP managed string buffers.

Control flow: `setup()` creates `faccessatdir/faccessatfile`, opens the directory and file, and prepares absolute/relative path strings. Three table cases call `faccessat(..., R_OK, 0)` expecting success.

State and persistence behavior: State is a tmpdir directory, a readable file, and open fds. Access checks do not modify persistent data.

Dependencies and integration points: Uses modern table-driven LTP tests with automatic buffers and tmpdir isolation.

Risks and test signals: Failures identify regressions in dirfd-relative, absolute, or cwd-relative access checks.
