# sources/test-tools/ltp/testcases/kernel/syscalls/fcntl/fcntl07.c

Purpose: verifies `FD_CLOEXEC` closes descriptors across `exec` for regular files, both ends of a pipe, and a FIFO.

Important APIs/types/functions: legacy LTP `test.h`, `option_t`, `fcntl(F_SETFD, FD_CLOEXEC)`, `fcntl(F_GETFD)`, `execlp`, `tst_fork`, `SAFE_PIPE`, `SAFE_MKFIFO`, and child mode option `-T`.

Control flow: normal mode opens a file, pipe, and FIFO. For each fd, `verify_cloexec()` sets `FD_CLOEXEC`, forks, and execs the same test binary with `-T fd`. Test mode calls `F_GETFD` on that numeric fd and returns zero only if it fails with `EBADF`, proving the fd was closed during exec.

State/persistence behavior: descriptor flags are changed on several fd types. The same executable is used as both parent test and child verifier.

Dependencies/integration: requires executable lookup by `TCID` in the test environment and legacy LTP safe macros.

Risks/test signals: environment path issues can look like test breakage. Functional failures are child reporting the fd remains open after exec.
