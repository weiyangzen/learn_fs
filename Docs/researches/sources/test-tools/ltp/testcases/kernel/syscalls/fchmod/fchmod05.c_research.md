# sources/test-tools/ltp/testcases/kernel/syscalls/fchmod/fchmod05.c

Purpose: verifies a non-root directory owner cannot set the setgid bit when its effective/supplementary groups do not match the directory group, while the rest of the requested mode is applied.

Important APIs/types/functions: `tst_get_free_gid`, `SAFE_SETGROUPS`, `SAFE_CHOWN`, `SAFE_SETEGID`, `SAFE_SETEUID`, `fchmod`, `SAFE_FSTAT`, and `PERMS_DIR`.

Control flow: setup creates `testdir`, assigns it to uid `nobody` and a free gid not equal to the user's group, sets supplementary/effective group and uid to `nobody`, and opens the directory. The test calls `fchmod(fd, 043777)` and expects the resulting mode to equal the requested mode with `S_ISGID` cleared.

State/persistence behavior: mutates process uid/gid/groups and directory ownership/mode. Cleanup restores effective uid/gid to root and closes the fd.

Dependencies/integration: root, account database, and a free gid are required.

Risks/test signals: sensitive to Linux setgid clearing rules. The comparison is strict and can expose unexpected special-bit behavior.
