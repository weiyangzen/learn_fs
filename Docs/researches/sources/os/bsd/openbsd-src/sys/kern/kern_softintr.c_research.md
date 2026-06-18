# File Research: sources/os/bsd/openbsd-src/sys/kern/kern_softintr.c

Purpose: Machine-independent soft interrupt implementation enabled under `__USE_MI_SOFTINTR`.

Key behavior:
- Defines `softintr_hand` with function, argument, runner CPU, level, flags, and state bits.
- `softintr_init()` initializes per-level queues.
- `softintr_establish()` maps IPL values to soft interrupt levels, allocates a handler, and records whether it is MPSAFE.
- `softintr_schedule()` queues a pending handler and calls machine `softintr()` while SPL is high, or marks restart if currently running.
- `softintr_dispatch()` drains a level queue, clears pending, records runner, runs with or without kernel lock depending on `SIF_MPSAFE`, handles restart, and increments `uvmexp.softs`.
- `softintr_disestablish()` marks dying, removes pending work, waits for a current runner through `sched_barrier()`, then frees.

Concurrency:
- All queues and handler state are protected by `softintr_lock`.
- Restart state prevents lost schedules while a handler is active.
- Disestablish uses scheduler barrier to avoid freeing a running handler.

Filesystem relevance:
- No direct filesystem logic. It is interrupt-bottom-half infrastructure used by drivers and networking/storage paths that can feed filesystem I/O.
