# sources/test-tools/ltp/testcases/kernel/syscalls/fcntl/fcntl11.c

Purpose: detailed record-lock splitting/coalescing test for adding read locks around existing write locks. It verifies `F_GETLK` reports the correct blocking subrange after parent lock transformations.

Important APIs/types/functions: `fcntl(F_SETLK)`, `fcntl(F_GETLK)`, `struct flock`, `F_WRLCK`, `F_RDLCK`, `F_UNLCK`, pipes for parent/child requests, `mkstemp`, `SAFE_PIPE`, `SAFE_WRITE`, `SAFE_READ`, and helper functions `do_lock`, `do_test`, `compare_lock`, `unlock_file`.

Control flow: setup creates a temp file with known content and pipes. Parent forks a child that repeatedly receives a `struct flock`, calls `F_GETLK`, and returns the result. The parent runs nine blocks that place write/read locks at adjacent, overlapping, nested, and separated byte ranges, asks the child to query conflicts, compares type/whence/start/len/pid, then unlocks all.

State/persistence behavior: uses process-associated POSIX locks on one file, with the child as an external observer so parent-owned locks are visible. Pipe messages are the synchronization state.

Dependencies/integration: legacy LTP harness, fork, pipes, and signal handling for unexpected child death.

Risks/test signals: complex range math and POSIX lock merging semantics. Failures pinpoint wrong lock type, range start/length, or pid after transformations.
