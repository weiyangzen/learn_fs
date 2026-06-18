# File Research: sources/os/bsd/freebsd-src/sys/kern/subr_epoch.c

## Purpose
Implements FreeBSD's epoch reclamation subsystem on top of Concurrency Kit epochs. It provides non-preemptible and preemptible epoch sections, grace-period waits, deferred callbacks, and callback draining.

## Key Elements
- Per-epoch structure: `struct epoch`.
- Per-CPU records: `struct epoch_record`.
- Global epochs: `global_epoch`, `global_epoch_preempt`.
- Lifecycle: `epoch_alloc()`, `epoch_free()`.
- Entry/exit: `epoch_enter()`, `epoch_exit()`, `_epoch_enter_preempt()`, `_epoch_exit_preempt()`.
- Grace waits: `epoch_wait()`, `epoch_wait_preempt()`.
- Deferred callbacks: `epoch_call()`, `epoch_call_task()`.
- Drain path: `epoch_drain_callbacks()`.
- Optional tracing under `EPOCH_TRACE`.
- Stats sysctls under `kern.epoch.stats`.

## Behavior
Initialization creates a per-CPU UMA zone, attaches per-CPU group tasks for callback processing, initializes counters, and allocates the global epochs. Each epoch owns per-CPU CK records and a drain lock pair.

Non-preemptible epoch sections enter a critical section and use the current CPU record. Preemptible epoch sections pin the thread, add an `epoch_tracker` to the CPU record's thread list, and call CK begin/end with a section object.

`epoch_wait_preempt()` may migrate to the CPU with blocking epoch participants, boost priorities, wait through turnstiles, or voluntarily switch to let blockers run. `epoch_call()` queues callbacks on the current CPU record and the per-CPU task polls all active epochs for deferred callbacks.

## Research Notes
The preemptible wait path is scheduler-aware and much more complex than the non-preemptible spin path. `epoch_free()` first drains callbacks, marks the epoch unused, then waits through `global_epoch` so callback tasks stop observing it before freeing per-CPU records.
