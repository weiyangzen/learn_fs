# File Research: sources/os/plan9/plan9/sys/src/9/port/proc.c

Implements the core portable process scheduler, sleep/wakeup, process allocation, exit/wait, notes, and process diagnostics.

Scheduler:
- Uses priority queues `runq[Nrq]` with bitmap `runvec`.
- `schedinit` handles returning from a process to the scheduler and freeing moribund processes.
- `sched` context-switches between `up` and `m->sched`, respects delayed scheduling while locks are held, and switches MMU state.
- `ready`, `queueproc`, `dequeueproc`, and `runproc` manage runnable processes with affinity and wired-CPU constraints.
- `hzsched`, `preempted`, `yield`, and `rebalance` handle periodic/preemptive/cooperative scheduling.
- `updatecpu` and `reprioritize` implement decaying CPU accounting and fair-share priority adjustment.
- EDF hooks are integrated through `edfready`, `edfrun`, `edfrecord`, and `edfstop`.

Process lifecycle:
- `procinit0` allocates the process arena.
- `newproc` initializes a fresh `Proc`, pid/note ids, kernel stack, identity strings, scheduling fields, and default state.
- `pexit` tears down fd/env/rendez/name groups, dot channel, segments, wait records, debuggers, pid hash, and finally enters `Moribund`.
- `pwait` waits for child exit records.
- `kproc` creates kernel processes inheriting selected state from `up`.

Sleep/notes:
- `sleep` atomically links a process to a `Rendez`, tests the condition, and switches to scheduler.
- `wakeup` readies a sleeping process and validates rendezvous state.
- `tsleep` layers relative timers over `sleep`.
- `postnote` queues notes, wakes sleeping processes, and pulls processes out of `Rendezvous` state.
- `procctl` handles `/proc` controls: stop, trace, exit, and insufficient-memory exit.

Diagnostics and support:
- `dumpaproc`, `procdump`, `scheddump`, `procflushseg`.
- `noprocpanic` dumps processes and exits on process exhaustion unless configured otherwise.
- `error`, `nexterror`, and `exhausted` implement kernel error unwinding helpers.
- `killbig` selects and kills a large process under memory pressure.
- `renameuser`, `accounttime`, `procindex`, pid hash helpers.

Cautions:
- Many routines require high interrupt priority or precise lock ordering.
- `sched` intentionally delays rescheduling while locks are held, except for moribund paths and critical allocator locks.
