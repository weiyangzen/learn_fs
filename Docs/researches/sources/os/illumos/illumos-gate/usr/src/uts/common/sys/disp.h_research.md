# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/disp.h

This header defines dispatcher queue structures, scheduler priority bounds, kernel preemption helpers, and dispatcher function declarations. It includes priocntl, thread, and scheduling class definitions.

`dispq_t` represents one dispatcher queue entry with first/last thread pointers and runnable count. `disp_t` is the per-CPU dispatcher state: queue pointer, lock, runnable count, current max run priority, max unbound priority, queue limit, last rundown time, steal counters, kernel-preemption queue data, owning CPU pointer, and related state.

Priority constants define system class priority bounds. `DISP_MAXRUNPRI()` reads a thread’s dispatcher queue max priority. Kernel globals include swapped thread count, no-steal timing, idle/preemption hooks, and dispatcher enqueue hooks.

Function declarations cover queue allocation/free, dequeue, initialization, class registration, interrupt state checks, preemption/switch/resume paths, run queue enqueue variants, CPU rechoose/surrender, kernel preemption, CPU selection, bound-thread checks, CPU dispatcher lifecycle, priority adjustment, swapped enqueue, and work detection. `KPREEMPT_SYNC`, `kpreempt_disable`, `kpreempt_enable`, and `CPU_IDLE_PRI` define preemption controls.

Research notes:
- This header belongs to the scheduler/dispatcher rather than DDI, but appears in the same sys header group.
- Several functions are low-level context-switch paths and include `__NORETURN` declarations.
- Dispatcher structure layout is kernel-private and CPU/scheduler sensitive.
