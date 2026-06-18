# File Research: sources/os/bsd/netbsd-src/sys/kern/subr_lockdebug.c

Read completely: 1096 lines.

Implements shared lock-debugging infrastructure for NetBSD lock primitives. With `LOCKDEBUG`, each initialized lock can get a `lockdebug_t` record stored in an RB tree by lock address and tracked on per-LWP or per-CPU held-lock lists.

Core behavior:
- `lockdebug_alloc()` allocates and registers a debug record at lock initialization, using an early static batch and later kmem-allocated batches.
- `lockdebug_free()` removes a record at lock destruction and panics if the lock is still held or shared.
- `lockdebug_wantlock()`, `lockdebug_locked()`, and `lockdebug_unlocked()` track attempted, acquired, and released locks, detecting recursion, interrupt-context sleep-lock acquisition, wrong-owner unlock, double-lock, and unlock-without-lock errors.
- `lockdebug_barrier()` verifies no unexpected spin/sleep/shared locks are held at barrier points.
- `lockdebug_mem_check()` checks whether a memory region being freed contains an active lock.
- DDB helpers print one lock, all locks by LWP/CPU, stack traces, and aggregate lock stats.
- `lockdebug_abort()` provides a fallback diagnostic path even without full `LOCKDEBUG`.

Concurrency and risks:
- Global modification uses `ld_mod_lk`; RB-tree lookup is protected through per-CPU lockdebug locks.
- The allocator must avoid unbounded recursion because allocating debug records can itself initialize locks.
- Once a lockdebug panic starts, `ld_panic` suppresses further diagnostics because state may be stale.
- KCOV is silenced around some lookup/memory-check paths to avoid instrumentation recursion.
