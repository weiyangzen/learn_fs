# sources/test-tools/ltp/testcases/kernel/syscalls/fchmod/fchmod06.c

Purpose: negative `fchmod(2)` errno matrix covering permission denial, bad descriptor, and read-only filesystem behavior.

Important APIs/types/functions: `SAFE_OPEN`, `SAFE_CLOSE`, `SAFE_SETEUID`, `SAFE_GETPWNAM`, `TST_EXP_FAIL`, `.needs_rofs`, and `fchmod`.

Control flow: setup opens a file on the read-only mount, creates two temp files, closes one descriptor to make it invalid, and switches euid to `nobody`. The test table expects `EPERM` on a file not owned by the unprivileged user, `EBADF` on the closed fd, and `EROFS` on the read-only mount fd.

State/persistence behavior: maintains three fds with distinct validity/ownership/filesystem states and changes process euid. The read-only mount is provisioned by LTP.

Dependencies/integration: requires root, read-only filesystem support, and tempdir/mountpoint management.

Risks/test signals: ordering of permission checks can be filesystem-dependent, especially for read-only mounts. The expected errno must match exactly.
