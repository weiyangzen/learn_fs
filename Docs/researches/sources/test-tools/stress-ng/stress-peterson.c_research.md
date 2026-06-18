# sources/test-tools/stress-ng/stress-peterson.c

Purpose: `stress-peterson.c` implements the `peterson` stressor, validating Peterson's two-process mutual exclusion algorithm under explicit memory fences and architecture barriers.

Important APIs/types/functions: `peterson_mutex_t` contains volatile `turn`, `check`, and two flags. `peterson_t` is shared and cache-aligned, containing the mutex and two metric slots. `peterson_mfence()` wraps `shim_mfence()`, and `peterson_mbarrier()` uses ARM `dmb sy` when present. `stress_peterson_p0()` increments the check value; `stress_peterson_p1()` decrements it and increments bogo ops.

Control flow: support probing installs a temporary SIGILL handler and executes the memory barrier path to ensure it is usable. The stressor mmaps shared state, synchronizes, initializes flags, records the parent CPU, and forks. The child optionally moves to the parent CPU and repeatedly enters the p0 side; the parent runs p1. Each side sets its flag, gives turn to the other, fences, waits until the critical section is allowed, updates `check`, clears its flag, records timing, and verifies the check changed exactly by one.

State and persistence behavior: shared anonymous memory holds the lock variables, check counter, and metrics. The only persistent process effect is temporary affinity adjustment in the child. Cleanup kills/waits the child and unmaps shared memory.

Dependencies and integration points: it requires shim memory fencing and siglongjmp support, optional architecture barriers, affinity helpers, mmap helpers, fork/kill helpers, scheduler helpers, and registers as CPU cache plus IPC with `VERIFY_ALWAYS`.

Risks: the algorithm is sensitive to memory ordering; weakly ordered architectures rely on the fence/barrier placements. A child exit status overwrites parent result if the child exits normally. If fork fails after mmap, the current code returns no-resource without unmapping the shared mapping, a small error-path leak.

Test signals: `--peterson` should produce `nanosecs per mutex` and no check mismatch. Useful coverage includes ARM/PPC/RISC-V fence behavior, SIGILL support skip, same-CPU affinity changes, and forced stop while the peer is spinning.
