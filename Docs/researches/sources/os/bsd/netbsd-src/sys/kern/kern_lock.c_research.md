# File Research: sources/os/bsd/netbsd-src/sys/kern/kern_lock.c

Read completely: 469 lines.

Implements the legacy global kernel lock, sleepability assertions, lock debug hooks, spinout diagnostics, and nested acquire/release accounting. This file is central to code paths that still rely on the big kernel lock while coexisting with adaptive mutexes, preemption, lockstat, and DTrace probes.

Core state:
- `kernel_lock_cacheline` stores the simple lock and volatile holder CPU on a cacheline-aligned object; `kernel_lock` is a strong alias.
- `kernel_lock_holder` records the CPU that most recently acquired the lock.
- `kernel_lock_dodebug` tracks lockdebug registration state.
- SDT probes record kernel lock entry and exit with the number of holds.

Sleepability:
- `assert_sleepable()` panics if called from idle context, hard interrupt, soft interrupt, or a pserialize read section, except during panic. It avoids changing preemption state and samples `lwp_pctr()` until stable before checking idle state.

Initialization and debug:
- `kernel_lock_init()` initializes the simple lock and registers it with lockdebug.
- `_kernel_lock_dump()` prints current CPU biglock count and waiter pointer for lockdebug/DDB-style diagnostics.
- `kernel_lock_trace_ipi()` prints and optionally stacktraces the CPU that is holding the kernel lock too long.
- `kernel_lock_spinout()` rate-limits reports, identifies the holder CPU, avoids self-reporting races, sends an IPI to collect the holder stack, and triggers a lockdebug abort in LOCKDEBUG kernels.

Acquire path:
- `_kernel_lock(nlocks)` raises to `splvm()`, handles recursive acquisition by incrementing per-CPU `ci_biglock_count` and LWP `l_blcnt`, and otherwise tries the simple lock fast path.
- On contention, it sets `ci_biglock_wanted` with memory barriers to coordinate with adaptive mutex owner/waiter logic, records lockstat spin timing, spins with backoff while temporarily lowering/restoring IPL, reports spinout after 10 seconds once init exec has started, then records holder/count/debug state after acquiring.
- After acquisition, it restores the previous wanted pointer with atomic swap and a matching memory barrier so mutex waiters see consistent ordering.

Release path:
- `_kernel_unlock(nlocks, countp)` releases one, all, or the special `-1` hold, updates LWP/per-CPU hold counts, fully unlocks the simple lock when the count reaches zero, optionally preempts if `l_dopreempt` is set, emits the exit SDT probe, and returns the previous hold count through `countp`.
- `_kernel_locked_p()` reports the raw simple-lock state.

Concurrency and integration:
- Per-LWP `l_blcnt` and per-CPU `ci_biglock_count` implement nesting and ownership accounting.
- Memory barriers around `ci_biglock_wanted` are paired with adaptive mutex entry/exit ordering.
- Lockstat records spin time for initial acquisition, not recursive holds.
- DTrace SDT probes, lockdebug, DDB, IPIs, preemption, and SPL handling all participate in diagnostics and correctness.

Risks and notes:
- The source explicitly warns that `_kernel_lock()` behavior is relied on by much of the kernel.
- `kernel_lock_holder` is diagnostic and can be unreliable without holding the lock; spinout code treats it cautiously.
- `_kernel_unlock()` asserts `nlocks < 2`, with zero meaning release all and `-1` meaning release exactly one from a single-hold state.
