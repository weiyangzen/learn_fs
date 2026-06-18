# sources/test-tools/ltp/testcases/kernel/syscalls/fcntl/fcntl20.c

Purpose: companion to `fcntl19.c` for read locks. It verifies unlocking sections around an existing read lock trims or splits the remaining read-lock regions correctly.

Important APIs/types/functions: `fcntl(F_SETLK)`, `fcntl(F_GETLK)`, `struct flock`, `F_RDLCK`, `F_WRLCK` probe locks, `F_UNLCK`, pipe helpers, `mkstemp`, `do_lock`, `do_test`, `compare_lock`, and `unlock_file`.

Control flow: setup creates the temp file and child query process. Parent runs seven blocks that place a read lock and unlock ranges before, overlapping the front, in the middle, overlapping the end, at the last byte, and past the end. The child queries with a write-lock request so read locks are reported as conflicts, and parent checks the resulting ranges.

State/persistence behavior: manipulates parent-owned read locks while a child process observes them. State is reset with a whole-file unlock after each block.

Dependencies/integration: legacy LTP, fork, pipes, tempdir, signal handling.

Risks/test signals: exact read-lock range splitting is the focus. Failures indicate wrong remaining read-lock extent, unexpected unlocked areas, or synchronization failure.
