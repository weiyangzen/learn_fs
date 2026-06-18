# File Research: sources/os/bsd/openbsd-src/sys/kern/kern_smr.c

Purpose: Implements safe memory reclamation deferred callbacks and grace-period waiting.

Key behavior:
- `smr_startup()` initializes the global deferred queue, WITNESS object, and wakeup timeout.
- `smr_startup_thread()` creates the `smr` kernel thread.
- `smr_thread()` waits for deferred callbacks, optionally pauses to batch work, waits for a grace period, then invokes each callback under WITNESS tracking.
- Long dispatch periods are rate-limited logged and tracepoints report latency/count.

Grace period model:
- `smr_grace_wait()` advances `smr_grace_period`, records it for the current CPU, then pegs the current process to each running CPU that has not crossed the period.
- `smr_idle()` dispatches local deferred callbacks and records quiescent-state grace-period progress with memory ordering.
- `smr_call_impl()` queues a callback on the current CPU deferred list and can expedite wakeup.
- `smr_barrier_impl()` waits until a queued callback has run using a `cond`.

Concurrency:
- Global queue protected by `smr_lock`.
- Per-CPU queues are dispatched at high IPL.
- MP builds use scheduler pegging and per-CPU grace-period counters; non-MP grace wait is effectively empty.

Filesystem relevance:
- Provides reclamation infrastructure suitable for lockless readers and deferred object teardown in kernel subsystems, including filesystem-adjacent caches and vnode-like structures.
