# sources/test-tools/ltp/testcases/kernel/syscalls/faccessat2/faccessat202.c

Purpose: Negative/error coverage for `faccessat2()` including bad address, invalid flags/mode, invalid fd, non-directory fd, and effective-id permission denial.

Important APIs/types/functions: `faccessat2`, `tst_get_bad_addr`, `SAFE_SETEUID`, `SAFE_GETPWNAM("nobody")`, `TST_EXP_FAIL`, `AT_EACCESS`, and root-required setup.

Control flow: `setup()` creates a 0444 file under a directory, opens the file, records a bad pointer and nobody user. Each row calls `faccessat2` with expected errno; the `EACCES` case temporarily switches euid to nobody and restores root.

State and persistence behavior: State includes tmpdir permissions, a regular-file dirfd, a bad userspace pointer, and effective uid transitions.

Dependencies and integration points: Requires root to change euid and create controlled permission scenarios.

Risks and test signals: Wrong errno or failure to restore euid would compromise later cases. The `AT_EACCESS` case specifically checks effective credential handling.
