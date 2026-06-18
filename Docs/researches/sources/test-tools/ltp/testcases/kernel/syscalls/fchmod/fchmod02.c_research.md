# sources/test-tools/ltp/testcases/kernel/syscalls/fchmod/fchmod02.c

Purpose: verifies root can use `fchmod(2)` to set broad permissions including sticky/setuid/setgid bits on a file not owned by root when the process group matches the file group.

Important APIs/types/functions: `SAFE_GETPWNAM`, `SAFE_GETGRNAM_FALLBACK`, `SAFE_OPEN`, `SAFE_CHOWN`, `SAFE_SETGID`, `fchmod`, `SAFE_FSTAT`, and `PERMS` from `fchmod.h`.

Control flow: setup creates `testfile`, changes ownership to `nobody` and a fallback group, then sets the process gid to that group. The test calls `fchmod(fd, 01777)` and verifies the resulting file mode matches `PERMS` after masking `S_IFREG`.

State/persistence behavior: mutates file ownership, process gid, and file mode. The fd remains open until cleanup.

Dependencies/integration: requires root and known users/groups. It relies on LTP account lookup and tempdir isolation.

Risks/test signals: group/user availability and filesystem special-bit handling can affect results. A syscall failure or incorrect mode is a failure.
