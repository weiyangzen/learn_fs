# File Research: sources/os/bsd/openbsd-src/sys/sys/sched.h

Defines CPU state accounting and kernel scheduler per-CPU state/API.

Key contents:
- CPU states: user, nice, system, spin, interrupt, idle.
- `struct cpustats` and online flag.
- Kernel `struct schedstate_percpu` with idle proc, run queues, dead proc queue, runtime, scheduler flags, CPU-time lock/counters, clock interrupt handles, run count, queue bitmap, spin state, SMR deferred state, and current priority.
- Scheduler flags for round-robin seen, should-yield, halt/halted, profclock, and itimer.
- Queue and priority constants: `SCHED_NQS`, `SCHED_PPQ`, `NICE_WEIGHT`, `ESTCPULIM`.
- CPU type flags for SMT/performance/efficiency classes.

Key APIs:
- Clock/scheduler lifecycle: `schedclock`, `roundrobin`, `scheduler_start`, `sched_init`, `sched_init_cpu`.
- Switching and CPU selection: `mi_switch`, `cpu_switchto`, `sched_chooseproc`, `sched_choosecpu`, `sched_choosecpu_fork`.
- Idle and CPU online/block controls.
- Runqueue operations `setrunqueue`, `remrunqueue`.
- Scheduler lock macros over `sched_lock`.

Risk notes:
- Per-CPU state mixes scheduler, clock, CPU accounting, and SMR deferral; field ownership annotations are important.
