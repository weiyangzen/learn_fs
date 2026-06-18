# sources/test-tools/ltp/testcases/kernel/syscalls/fchown/fchown01.c

Purpose: basic positive `fchown(2)` test on a file descriptor using the process effective uid and gid.

Important APIs/types/functions: `FCHOWN` compatibility macro, `UID16_CHECK`, `GID16_CHECK`, `SAFE_OPEN`, `SAFE_CLOSE`, `TST_EXP_PASS`, and `compat_tst_16.h`.

Control flow: setup validates current uid/gid for compatibility variants and opens `fchown01_testfile`. The test calls `FCHOWN(fd, uid, gid)` and expects success.

State/persistence behavior: creates a temp file and may update ownership to the same uid/gid. The descriptor is held globally and closed in cleanup.

Dependencies/integration: tempdir and 16-bit uid/gid compatibility layer.

Risks/test signals: minimal functionality check. Failure indicates `fchown` rejected a valid fd or the compatibility uid/gid is not usable.
