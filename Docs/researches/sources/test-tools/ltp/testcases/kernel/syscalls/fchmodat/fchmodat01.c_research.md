# sources/test-tools/ltp/testcases/kernel/syscalls/fchmodat/fchmodat01.c

Purpose: positive functionality test for `fchmodat(2)` with relative paths under a directory fd, absolute paths where dirfd is ignored, and `AT_FDCWD` relative paths.

Important APIs/types/functions: `fchmodat`, `SAFE_MKDIR`, `SAFE_OPEN`, `SAFE_LSTAT`, `tst_tmpdir_genpath`, LTP buffer allocation, and `AT_FDCWD`.

Control flow: setup creates `fchmodatdir/fchmodatfile`, opens the directory and file, and computes an absolute path. Each table case calls `fchmodat(*fd, *pathname, 0600, 0)`, then `lstat`s the full path and verifies the regular-file mode is `0600`.

State/persistence behavior: one file's mode is repeatedly set through different path resolution modes. Open directory and file fds are closed in cleanup.

Dependencies/integration: tempdir and dynamically managed strings from `tst_buffers`.

Risks/test signals: verifies path resolution plus mode mutation. Failures are syscall failure or mode mismatch after `lstat`.
