# sources/test-tools/ltp/testcases/kernel/syscalls/fcntl/fcntl13.c

Purpose: negative `fcntl(2)` argument validation for lock pointer faults, invalid commands, invalid `l_whence`, and invalid file descriptors.

Important APIs/types/functions: `fcntl`, `F_SETLK`, `F_GETLK`, `tst_get_bad_addr`, `struct flock`, `TST_EXP_FAIL2`, and errno constants `EFAULT`, `EINVAL`, `EBADF`.

Control flow: setup initializes a `struct flock` with invalid `l_whence = -1`. Each table case calls `fcntl` with the configured fd, command, and flock pointer; the null pointer case is replaced by an LTP bad address at runtime.

State/persistence behavior: no files are opened. Tests use fd `1` for argument validation and `-1` for bad-fd validation.

Dependencies/integration: modern LTP bad-address helper.

Risks/test signals: errno precedence depends on command validation order. Cases are separated to target one invalid condition each.
