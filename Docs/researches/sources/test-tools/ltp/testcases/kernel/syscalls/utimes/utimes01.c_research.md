<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/utimes/utimes01.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/utimes/utimes01.c

Purpose: verifies `utimes()` success for owner timestamp updates and expected failures for `EACCES`, `ENOENT`, `EFAULT`, `EPERM`, and `EROFS`.

Important APIs/types/functions: `tcases[]` pairs pathnames with `struct timeval` arrays and expected errno. `setup()` creates a root-owned inaccessible file, switches to `nobody`, and creates an owned file. `utimes_verify()` snapshots existing times for success cases, calls `utimes()`, checks `TST_ERR`, and restores the original timestamps.

Control flow/state: each case is independent. Success cases mutate `testfile1` timestamps using alternate atime/mtime arrays, then restore the prior values; negative cases exercise missing, NULL, non-owned, and read-only mount paths.

Dependencies/integration: requires root to switch euid and LTP `needs_rofs` for the read-only path. It uses the legacy LTP syscall harness macros rather than time64 variants.

Risks/test signals: the test checks errno through `TST_ERR`; unexpected success or wrong errno are the main signals. The restoration call can turn a success assertion into `TBROK` if timestamp restoration fails.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/utimes/utimes01.c -->
