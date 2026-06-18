# sources/test-tools/ltp/testcases/kernel/syscalls/faccessat2/faccessat201.c

Purpose: Positive coverage for the `faccessat2()` syscall, including `AT_EACCESS` and `AT_SYMLINK_NOFOLLOW`.

Important APIs/types/functions: `faccessat2` from `lapi/faccessat.h`, `SAFE_TOUCH`, `SAFE_SYMLINK`, `SAFE_OPEN(... O_DIRECTORY)`, `AT_FDCWD`, `AT_EACCESS`, `AT_SYMLINK_NOFOLLOW`, and `TST_EXP_PASS`.

Control flow: `setup()` creates a readable file and symlink. Seven table cases exercise dirfd-relative, absolute with bad fd, cwd-relative, effective-id mode, and symlink-no-follow access checks.

State and persistence behavior: Filesystem state is a tmpdir file with mode 0444 and a symlink. The syscall only observes permissions.

Dependencies and integration points: Depends on Linux 5.8+ syscall availability via the LTP lapi wrapper; unsupported syscall handling is centralized there.

Risks and test signals: Failures indicate wrong flag/path handling in `faccessat2`. Symlink behavior is a distinct signal from regular path resolution.
