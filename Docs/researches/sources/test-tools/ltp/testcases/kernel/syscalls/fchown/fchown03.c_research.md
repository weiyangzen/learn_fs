# sources/test-tools/ltp/testcases/kernel/syscalls/fchown/fchown03.c

Purpose: verifies a non-root file owner can change the group of a file to its effective group and that `fchown` clears setuid/setgid bits.

Important APIs/types/functions: `SAFE_GETPWNAM`, `SAFE_SETEGID`, `SAFE_SETEUID`, `SAFE_FCHOWN`, `SAFE_FCHMOD`, `FCHOWN`, `UID16_CHECK`, `GID16_CHECK`, `SAFE_STAT`, and helper checks `check_owner`/`check_mode`.

Control flow: setup switches effective gid/uid to `nobody` and creates the file. The test temporarily returns to root, sets file group to 0 and special bits, switches back to `nobody`, verifies initial state, calls `FCHOWN(fd, -1, gid)`, then verifies group changed and setuid/setgid bits cleared.

State/persistence behavior: toggles credentials, file group, and mode. Cleanup restores effective uid/gid to root and closes the fd.

Dependencies/integration: root and `nobody` account required. Uses compatibility wrappers for uid/gid width.

Risks/test signals: sensitive to supplementary group and privilege semantics. Wrong ownership or mode clearing fails.
