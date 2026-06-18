# sources/test-tools/ltp/testcases/kernel/syscalls/fchown/fchown04.c

Purpose: negative `fchown(2)` errno coverage for unprivileged ownership change, invalid fd, and read-only filesystem.

Important APIs/types/functions: `FCHOWN`, `UID16_CHECK`, `GID16_CHECK`, `SAFE_OPEN`, `SAFE_SETEUID`, `SAFE_GETPWNAM`, `TST_EXP_FAIL`, `.needs_rofs`, and errno constants `EPERM`, `EBADF`, `EROFS`.

Control flow: setup opens a normal file, opens the read-only mountpoint, then drops euid to `nobody`. Each test case calls `FCHOWN` using current effective uid/gid and expects the table errno.

State/persistence behavior: maintains one valid writable fd, one invalid fd initialized to `-1`, one rofs fd, and unprivileged credentials.

Dependencies/integration: root, read-only filesystem provisioning, tempdir, and uid/gid compatibility layer.

Risks/test signals: errno precedence is important for rofs and permission cases. Any unexpected success or errno mismatch fails.
