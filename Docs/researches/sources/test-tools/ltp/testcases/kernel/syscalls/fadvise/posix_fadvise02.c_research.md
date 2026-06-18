# sources/test-tools/ltp/testcases/kernel/syscalls/fadvise/posix_fadvise02.c

Purpose: Verifies `posix_fadvise()` returns `EBADF` for a deliberately invalid file descriptor across all defined advice values.

Important APIs/types/functions: `WRONG_FD` constant 42, `close()` retry handling, `posix_fadvise`, `EBADF`, and `tst_strerrno`.

Control flow: `setup()` closes fd 42 if open, tolerating `EBADF` and retrying on `EINTR`. Each testcase calls `posix_fadvise(42, ...)` and expects returned error number `EBADF`.

State and persistence behavior: State is the absence of a valid fd 42 in the process fd table.

Dependencies and integration points: Complements the valid-fd fadvise tests and uses the modern LTP test table.

Risks and test signals: If some previous harness setup reopens fd 42 after setup, the signal could be corrupted, but the test closes it immediately before the cases.
