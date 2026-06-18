# sources/test-tools/ltp/testcases/kernel/syscalls/fchmod/fchmod04.c

Purpose: verifies `fchmod(2)` succeeds on a directory and can set sticky/setuid/setgid-style permission bits when invoked by the directory owner.

Important APIs/types/functions: `SAFE_GETPWNAM`, `SAFE_MKDIR`, `SAFE_OPEN`, `fchmod`, `fstat`, `TST_EXP_PASS_SILENT`, and constants `TESTDIR`, `DIR_MODE`, `PERMS`.

Control flow: setup looks up `nobody`, creates `testdir`, and opens it read-only. The test calls `fchmod(fd, PERMS)` and verifies the resulting directory mode contains all requested permission bits.

State/persistence behavior: creates a temp directory and changes its mode through an open directory fd. Unlike the comment, setup does not switch uid in the current version, so root privileges remain unless inherited behavior changes.

Dependencies/integration: requires root and a tempdir. It depends on directory fds being accepted by `fchmod`.

Risks/test signals: possible mismatch between comment intent and implementation credential state. Failure is syscall failure or missing requested mode bits.
