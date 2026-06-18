# sources/test-tools/ltp/testcases/kernel/syscalls/fcntl/fcntl17.c

Purpose: validates kernel deadlock detection for blocking POSIX record locks. It orchestrates three children so two blocking lock requests form a delayed cycle and expects `EDEADLK`.

Important APIs/types/functions: `fcntl(F_SETLK)`, `fcntl(F_SETLKW)`, `fcntl(F_GETLK)`, `struct flock`, multiple pipes, `fork`, `alarm`, `SIGCHLD`/`SIGALRM` handlers, locks `lock1` through `lock5`, and helper messaging functions `parent_wait`, `child_free`, `stop_children`.

Control flow: setup creates pipes and a temp file. Parent forks three children, commands them to place initial disjoint write locks, verifies those locks with `F_GETLK`, then commands child 2 to block on child 3's range and child 3 to block on a range held by child 1/2. After child 1 releases, a deadlock should be detected and reported through the parent pipe as `EDEADLK`.

State/persistence behavior: child processes own distinct byte-range locks. Parent drives state transitions with pipe messages and uses an alarm to fail if deadlock detection never occurs.

Dependencies/integration: legacy LTP, fork, pipes, signals, and POSIX lock deadlock detection.

Risks/test signals: highly timing/order dependent but explicitly synchronized. Failure means wrong initial lock ownership, missing `EDEADLK`, timeout, or child death.
