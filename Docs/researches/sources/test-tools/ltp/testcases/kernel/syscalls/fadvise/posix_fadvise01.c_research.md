# sources/test-tools/ltp/testcases/kernel/syscalls/fadvise/posix_fadvise01.c

Purpose: Verifies `posix_fadvise()` returns 0 for every defined advice value.

Important APIs/types/functions: `posix_fadvise(fd, 0, 0, advice)`, advice constants `NORMAL`, `SEQUENTIAL`, `RANDOM`, `NOREUSE`, `WILLNEED`, `DONTNEED`, `SAFE_OPEN`, and `tst_strerrno`.

Control flow: `setup()` opens `/bin/cat` read-only. Each testcase calls `posix_fadvise` with one valid advice and expects return value 0 rather than `errno`.

State and persistence behavior: The open file descriptor is the only state; fadvise may update kernel caching hints but the test does not depend on persistent changes.

Dependencies and integration points: Uses LTP's syscall compatibility includes and table count over advice values.

Risks and test signals: Failures show invalid rejection of a permitted advice. The test assumes `/bin/cat` exists and is readable.
