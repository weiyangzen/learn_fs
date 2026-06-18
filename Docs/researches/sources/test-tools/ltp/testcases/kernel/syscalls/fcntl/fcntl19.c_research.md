# sources/test-tools/ltp/testcases/kernel/syscalls/fcntl/fcntl19.c

Purpose: detailed record-lock test for unlocking sections around an existing write lock. It verifies the kernel trims or splits write locks correctly after `F_UNLCK` ranges overlap different portions.

Important APIs/types/functions: `fcntl(F_SETLK)`, `fcntl(F_GETLK)`, `struct flock`, parent/child pipes, `mkstemp`, `do_lock`, `do_test`, `compare_lock`, `unlock_file`, `F_WRLCK`, and `F_UNLCK`.

Control flow: setup creates a temp file, writes alphabet data, and starts a child that answers `F_GETLK` queries. Parent runs seven blocks: unlock just before, ending at first byte, overlapping front, middle split, overlapping end, starting at last byte, and starting past end of a write lock. After each unlock, it asks the child to query conflicting write locks and compares the remaining lock regions.

State/persistence behavior: parent-owned write locks are mutated in place; the child observes them as an independent process. Unlock calls can shrink, split, or leave locks untouched depending on overlap.

Dependencies/integration: legacy LTP, fork, pipes, signal handler for child death, tempdir.

Risks/test signals: exact range arithmetic is the test target. Failures report wrong lock type/start/length/pid or unexpected child termination.
