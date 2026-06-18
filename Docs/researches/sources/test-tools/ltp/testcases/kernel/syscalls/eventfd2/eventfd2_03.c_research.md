# sources/test-tools/ltp/testcases/kernel/syscalls/eventfd2/eventfd2_03.c

Purpose: Validates eventfd semaphore mode by coordinating two forked processes through two `EFD_SEMAPHORE` descriptors.

Important APIs/types/functions: `eventfd2(0, EFD_SEMAPHORE)`, `SAFE_READ`, `SAFE_WRITE`, `SAFE_FORK`, `exit()`, and helper functions `xsem_wait`, `xsem_post`, and `sem_player`.

Control flow: The parent creates two semaphore eventfds and forks two children. Each child posts once to the other side, waits once, posts five units, then performs five waits on the opposite descriptor and reports success.

State and persistence behavior: The eventfd counters act as semaphores: each read consumes one unit instead of draining the full counter. Descriptors are inherited across fork.

Dependencies and integration points: Depends on eventfd2 syscall support and LTP child reaping through `.forks_child = 1`; no explicit parent assertions are needed beyond child results.

Risks and test signals: Deadlock would expose broken semaphore decrement semantics or lost fork inheritance. The test relies on the harness to reap both children after `.test_all` returns.
