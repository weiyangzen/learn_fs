# File Research: sources/os/bsd/dragonflybsd/sys/kern/usched_bsd4.c

## Purpose

`usched_bsd4.c` implements DragonFly BSD's original BSD4 user scheduler. It registers `usched_bsd4`, manages runnable user LWPs separately from the LWKT kernel-thread scheduler, maps real-time/normal/idle/thread priorities onto scheduler queues, tracks per-CPU current user-thread ownership, and uses helper threads plus IPIs to place runnable user threads on CPUs.

## Main Responsibilities

- Registers the `bsd4` scheduler through `struct usched usched_bsd4`.
- Maintains global run queues for realtime/FIFO, normal, and idle classes.
- Acquires and releases the per-CPU current user LWP when threads enter or leave userland.
- Computes dynamic user priorities from `rtprio`, `nice`, estimated CPU use, and batch behavior.
- Implements round-robin preemption and scheduler-clock CPU accounting.
- Selects CPUs for newly runnable LWPs using ready/current CPU masks, affinity masks, SMT hints, and optional cache-coherent topology heuristics.
- Starts per-CPU scheduler helper threads and exposes `kern.usched_bsd4.*` sysctls.

## Scheduling Model

The file defines `MAXPRI` as 128 and uses `NQS == 32`, so each scheduler queue covers four priority values. Normal LWPs use `lwp_usdata.bsd4` fields for `priority`, `rqindex`, `estcpu`, `batch`, and `rqtype`.

There are three global queue arrays:

- `bsd4_rtqueues[NQS]` for realtime/FIFO priorities.
- `bsd4_queues[NQS]` for normal priorities.
- `bsd4_idqueues[NQS]` for idle priorities.

Each queue class has a bitmask (`bsd4_rtqueuebits`, `bsd4_queuebits`, `bsd4_idqueuebits`) so the scheduler can find the first non-empty queue with bit scan operations. `bsd4_runqcount` tracks total queued LWPs, `bsd4_curprocmask` tracks CPUs with a designated current user LWP, and `bsd4_rdyprocmask` tracks CPUs ready to accept work.

## Core Control Flow

`bsd4_acquire_curproc()` is called before returning to userland. It removes the thread from sleep queues if needed, recalculates `estcpu`, handles pending user reschedule requests, and loops until the calling LWP becomes the per-CPU `uschedcp`. If it cannot run on the current CPU or loses to a better current LWP, it deschedules itself, queues itself through `bsd4_setrunqueue()`, and switches away. This function is explicitly allowed to migrate the thread.

`bsd4_release_curproc()` detaches the current LWP from the CPU's user scheduler slot, clears the current-CPU mask bit, sets `upri` to `PRIBASE_NULL`, and calls `bsd4_select_curproc()` to choose a replacement.

`bsd4_select_curproc()` chooses the next LWP from the global queues, optionally using the cache-coherent chooser. If it finds one, it marks the CPU as having a current user LWP, stores `uschedcp`, resets round-robin state, acquires the target LWKT thread, and schedules it.

`bsd4_setrunqueue()` validates the LWP state, gives away LWKT ownership, inserts the LWP into the global scheduler queue, then searches for a CPU to notify. It first prefers CPUs that are ready but not currently running a user thread, then CPUs running worse-priority user threads, and finally falls back to a rotating CPU. Remote CPUs are kicked with either an IPI reschedule or helper-thread wakeup.

## Priority and Accounting

`bsd4_schedulerclock()` runs at `ESTCPUFREQ` on each CPU. It requests user reschedule after `usched_bsd4_rrinterval`, increments `lwp_estcpu` toward `ESTCPUMAX`, asserts no active spinlocks, and calls `bsd4_resetpriority()`.

`bsd4_recalculate_estcpu()` decays or recomputes estimated CPU use based on elapsed scheduler ticks, the LWP's measured CPU ticks, system runnable pressure, and `usched_bsd4_decay`. It also updates `lwp_batch`: sustained CPU use makes a thread more batch-like, while low CPU use reduces batchiness.

`bsd4_resetpriority()` maps scheduling class to queue priority. Realtime/FIFO, idle, and thread classes use explicit `rtprio` values. Normal class combines `nice`, `estcpu`, and the batch adjustment, then moves an on-runqueue LWP between queues if its bucket changes. It also updates `td_upri` for LWKT's view of user threads running in the kernel and may trigger a reschedule if the LWP became more important than a CPU's current user LWP.

`bsd4_forking()` initializes child `estcpu` above the parent to make the child less desirable, starts child batch state at midpoint, and docks the parent slightly to limit fork-heavy workloads.

## CPU Selection and Topology

The default chooser, `bsd4_chooseproc_locked()`, scans realtime, normal, then idle queues for the best runnable LWP whose CPU mask includes the current CPU. It avoids replacing `chklp` unless the queued thread is meaningfully better and prefers a same-CPU candidate at equal queue priority when available.

`bsd4_chooseproc_locked_cache_coherent()` adds topology-aware behavior. It tries to keep threads near their home CPU/topology level, defers batch-like threads that would harm cache locality, records a "best of the worst" candidate when it must give up, and uses `bsd4_kick_helper()` to wake the LWP's preferred CPU instead of stealing unnecessarily.

The SMT path in `bsd4_setrunqueue()` prefers an idle physical core and uses sibling information from `cpu_topology` to avoid loading sibling logical CPUs when a better core exists.

## Initialization and Tunables

`bsd4_rqinit()` initializes the global queues and spinlock and enables CPU 0 for scheduling. `sched_thread_cpu_init()` creates per-CPU helper threads, records CPU topology nodes, enables ready/current masks, and creates `kern.usched_bsd4` sysctls.

Important tunables include `rrinterval`, `decay`, `batch_time`, `kicks`, `smt`, `cache_coherent`, `upri_affinity`, `queue_checks`, and `stick_to_level`. Debug state is exposed under `debug.bsd4_*`, and KTR events trace acquisition, release, runqueue placement, choosing, and helper behavior.

## Concurrency and Risk Notes

The scheduler depends on carefully paired critical sections, `bsd4_spin`, atomic CPU-mask updates, `LWP_MP_ONRUNQ`, LWKT deschedule/acquire/schedule operations, and IPI callbacks. The comments repeatedly identify migration-sensitive paths: `bsd4_acquire_curproc()` can migrate a thread even though most kernel code assumes stable CPU locality. Runqueue insertion loses ownership of the LWP once the spinlock is released, so priority changes, exits, or remote CPU selection can race unless state flags and locks are correct.

The global runqueue design creates contention around `bsd4_spin`, while the topology/cache-coherent logic adds heuristic complexity. CPU-mask edge cases are partly handled, including fallback behavior when `usched_global_cpumask` does not cover an LWP's allowed CPU mask.
