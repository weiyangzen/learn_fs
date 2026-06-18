# File Research: sources/os/bsd/openbsd-src/sys/sys/clockintr.h

This header defines the OpenBSD clock interrupt scheduling interface and statistics.

Key definitions:
- Public stats: `struct clockintr_stat`.
- Kernel platform API: `struct intrclock` with `ic_rearm` and `ic_trigger`.
- Schedulable callback: `struct clockintr`, with pending/all queue links and callback function.
- Rescheduling request: `struct clockrequest`.
- Per-CPU queue: `struct clockqueue`, including mutex, pending lists, hardclock handle, interrupt clock, stats, generation counters, and dispatch flags.

Kernel APIs:
- CPU/platform: `clockintr_cpu_init`, `clockintr_dispatch`, `clockintr_trigger`.
- Callback lifecycle: `clockintr_bind`, `clockintr_schedule`, `clockintr_cancel`, `clockintr_unbind`, `clockintr_stagger`.
- Request helpers: `clockintr_advance`, `clockrequest_advance`, `clockrequest_advance_random`.
- Queue/sysctl: `clockqueue_init`, `sysctl_clockintr`.

Risk notes:
- Lock annotations in comments are central to correctness: queue fields are split between immutable, mutex-protected, atomic, and CPU-owned state.
- `clockrequest` lets callbacks ask for rescheduling on return, so dispatch paths must honor ownership and `CQ_IGNORE_REQUEST`.
