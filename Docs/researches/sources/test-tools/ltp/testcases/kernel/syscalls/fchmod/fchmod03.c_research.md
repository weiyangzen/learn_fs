# sources/test-tools/ltp/testcases/kernel/syscalls/fchmod/fchmod03.c

Purpose: verifies a non-root owner can successfully change mode on its own regular file and set the sticky/setuid/setgid bits requested by `PERMS`.

Important APIs/types/functions: `SAFE_GETPWNAM`, `SAFE_SETEUID`, `SAFE_OPEN`, `fchmod`, `fstat`, `TST_EXP_PASS_SILENT`, and constants from `fchmod.h`.

Control flow: setup looks up `nobody`, switches effective uid, and creates `testfile`. The test calls `fchmod(fd, PERMS)`, stats the fd, and verifies all requested `PERMS` bits are present.

State/persistence behavior: process effective uid is changed and a temp file's mode is modified. Cleanup closes the fd but does not restore euid explicitly, relying on process exit.

Dependencies/integration: requires root to switch to `nobody`, tempdir setup, and normal Linux owner permission semantics.

Risks/test signals: the check uses `(file_mode & PERMS) == PERMS`, so extra file-type bits are tolerated. Failure indicates either syscall rejection or missing requested permission bits.
