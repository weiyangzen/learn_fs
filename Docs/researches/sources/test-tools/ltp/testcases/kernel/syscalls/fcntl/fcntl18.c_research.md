# sources/test-tools/ltp/testcases/kernel/syscalls/fcntl/fcntl18.c

Purpose: legacy negative `fcntl(2)` test for `EFAULT` on bad flock pointers and `EINVAL` on invalid commands, including an unprivileged child path.

Important APIs/types/functions: `fcntl`, `F_GETLK`, invalid pointer cast `(struct flock *)-1`, invalid command `-1`, `tst_fork`, `setreuid`, `getpwnam("nobody")`, and legacy LTP root/tempdir helpers.

Control flow: setup requires root and creates a tempdir. Block 1 opens `temp.dat` and expects `F_GETLK` with an invalid pointer to set `EFAULT`. Block 2 repeats the `EFAULT` check. Block 3 forks a child, drops it to `nobody`, calls `fcntl(fd, -1, &fl)`, and expects `EINVAL`; parent checks child exit status.

State/persistence behavior: opens one temp file and changes child credentials only. The file remains open until cleanup.

Dependencies/integration: requires root and a `nobody` account. Uses legacy LTP APIs.

Risks/test signals: the repeated EFAULT blocks are redundant. The code does not reset errno before every call, so correctness relies on failed calls setting errno as expected.
