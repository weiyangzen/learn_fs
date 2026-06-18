# File Research: sources/os/bsd/dragonflybsd/sys/kern/subr_sleepqueue.c

## Summary
Implements a FreeBSD-compatible `sleepq*()` API shim on top of DragonFly’s `tsleep` wait-channel/domain mechanisms.

## Main Responsibilities
- Initializes a 1024-bucket wait-channel hash table and object cache for `sleepqueue_wchan`.
- `sleepq_lock()` creates/refs and spin-locks a wait-channel record.
- `sleepq_release()` drops refs, recycles/free-lists idle records, and unlocks.
- `sleepq_add()` records current-thread sleepqueue state and calls `tsleep_interlock()`.
- Supports timeout setup, sleeper counts, wait variants, type query, signal, and broadcast.
- Provides no-op thread setup/teardown hooks for compatibility.

## Important Behavior
The implementation records state in `struct thread` and enacts the actual sleep only on `sleepq_wait*()`. Queue numbers map to DragonFly domains `PDOMAIN_FBSD0 + queue * PDOMAIN_FBSDINC`. Free wchan records are retained per bucket up to `SLEEPQ_FREEPERSLOT`.

## Risks
The file explicitly says this is for FreeBSD compatibility, such as Linux KPI code. It assumes callers follow the FreeBSD lock/add/wait/release protocol. The `lock_object` invariant association mentioned in comments is not implemented.
