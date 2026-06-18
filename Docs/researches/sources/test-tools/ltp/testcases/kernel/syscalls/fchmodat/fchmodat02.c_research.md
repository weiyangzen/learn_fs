# sources/test-tools/ltp/testcases/kernel/syscalls/fchmodat/fchmodat02.c

Purpose: negative `fchmodat(2)` errno coverage for invalid dirfd/path/flag combinations.

Important APIs/types/functions: `fchmodat`, `tst_get_bad_addr`, `PATH_MAX`, `TST_EXP_FAIL`, `SAFE_OPEN`, LTP buffers, and errno constants `ENOTDIR`, `EBADF`, `EFAULT`, `ENAMETOOLONG`, `ENOENT`, `EINVAL`.

Control flow: setup creates and opens a regular file, assigns a bad user pointer, and fills an overlong pathname buffer. Each table case calls `fchmodat` with the configured fd, pathname pointer, and flags, expecting the specific errno.

State/persistence behavior: maintains one open regular-file fd and fixed path buffers. No successful chmod should occur.

Dependencies/integration: tempdir and LTP bad-address helper.

Risks/test signals: errno precedence may be kernel-sensitive when several arguments are invalid. The table is designed so each case isolates one error path.
