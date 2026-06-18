# File Research: sources/os/bsd/netbsd-src/sys/kern/kern_runq.c

## Purpose

`kern_runq.c` implements NetBSD’s machine-independent scheduler run queue mechanics: per-CPU priority queues, enqueue/dequeue, preemption requests, multiprocessor CPU selection, load stealing, idle balancing, scheduler stats, next-LWP selection, sysctl tunables, and DDB runqueue printing.

## Main Responsibilities

- Initializes scheduler balancing tunables:
  - `cacheht_time`
  - `min_catch`
  - `skim_interval`
- Attaches per-CPU scheduler state with `sched_cpuattach()`.
- Maintains per-priority `TAILQ` run queues per CPU.
- Tracks non-empty priorities through bitmaps and `spc_maxpriority`.
- Handles preemption signaling:
  - `sched_resched_cpu()`
  - `sched_resched_lwp()`
- Handles multiprocessor migration and stealing:
  - `sched_takecpu()`
  - `sched_idle()`
  - `sched_preempted()`
  - `sched_vforkexec()`
- Selects next runnable LWP with `sched_nextlwp()`.
- Exposes scheduler tunables via `kern.sched`.

## Run Queue Data Model

- Each CPU has `struct schedstate_percpu`.
- Runnable LWPs are queued by effective priority `lwp_eprio(l)`.
- `spc_bitmap[]` tracks which priority queues are non-empty.
- `spc_count` tracks all runnable LWPs on that CPU.
- `spc_mcount` tracks migratable runnable LWPs, updated atomically for low-cost remote checks.
- `spc_maxpriority` stores the highest runnable priority currently present.

## Enqueue and Dequeue

- `sched_enqueue()`:
  - requires the LWP locked by its CPU scheduler mutex;
  - marks the priority bit when inserting into an empty priority queue;
  - inserts at head/tail depending on scheduling class and preemption state:
    - `SCHED_OTHER`: tail;
    - `SCHED_FIFO`: head when preempting;
    - `SCHED_RR`: head or tail depending on round-robin tick use;
  - clears `SPCF_IDLE`;
  - updates counts and max priority;
  - calls `sched_newts()`.
- `sched_dequeue()`:
  - removes the LWP from its priority queue;
  - clears priority bitmap if queue becomes empty;
  - recomputes `spc_maxpriority` by scanning bitmap words downward;
  - clears `spc_migrating` if the dequeued LWP was pending migration.

## Preemption

- `sched_resched_cpu()`:
  - compares incoming priority with current CPU priority;
  - chooses idle, user-preempt, or kernel-preempt request flags;
  - sets `DOPREEMPT_ACTIVE` for kernel preemption when supported;
  - drops scheduler lock before poking `ci_want_resched`/remote CPU where requested to avoid remote wakeups immediately blocking on the same lock.
- `sched_resched_lwp()` derives target CPU and effective priority from an LWP in `LSRUN`.

## Multiprocessor CPU Selection

- `sched_migratable()` rejects offline CPUs, enforces explicit CPU affinity, and enforces processor-set ID matching.
- `lwp_cache_hot()` treats newly created LWPs as hot and otherwise checks recent runtime against `cacheht_time`.
- `sched_bestcpu()` scans CPU packages/cores to find the best CPU:
  - prefers idle first-class CPUs;
  - otherwise chooses lowest competing priority;
  - breaks ties by CPU class and runqueue length.
- `sched_takecpu()`:
  - keeps bound LWPs on their CPU;
  - spreads newly created LWPs across packages except special vfork cases;
  - prefers idle sibling/core CPUs;
  - keeps cache-hot `SCHED_OTHER` LWPs sticky when reasonable;
  - falls back to `sched_bestcpu()`.

## Idle Stealing and Migration

- `sched_catchlwp()` attempts to steal a migratable LWP from another CPU’s runqueue, avoiding bound/cache-hot LWPs under gentle stealing.
- `sched_idle_migrate()` completes pending `l_target_cpu` migrations from the idle loop, double-locking runqueues in address order/trylock fallback to avoid deadlock.
- `sched_steal()` performs low-cost checks before double-locking two CPUs.
- `sched_idle()`:
  - handles pending migrations first;
  - returns if CPU is offline or has local work;
  - steals first from SMT siblings;
  - then scans packages subject to `skim_interval` rate limiting.

## Preempted and Vfork Handling

- `sched_preempted()` may set `l_target_cpu` for an LWP that yielded/preempted on a second-class CPU or a vfork child marked for teleport.
- `sched_vforkexec()` marks a vfork child for teleport and calls `preempt()` when appropriate.

## Scheduler Stats and Next LWP

- `sched_lwp_stats()` updates sleep time, CPU-bound `LW_BATCH` state, resets tick sums, calls scheduler-specific hooks, and updates DTrace `curthread`.
- `sched_nextlwp()`:
  - updates current LWP runtime sum;
  - returns idle if migration is pending or no runqueue entries exist;
  - selects first LWP from highest-priority queue;
  - calls `sched_oncpu()` and stamps `l_rticks`.

## Sysctl and Debugging

- `SYSCTL_SETUP(sysctl_sched_setup)` registers:
  - `kern.sched.cacheht_time`
  - `kern.sched.skim_interval`
  - `kern.sched.min_catch`
  - `kern.sched.timesoftints`
  - `kern.sched.kpreempt_pri`
- Under DDB, `sched_print_runqueue()` prints per-CPU runqueue state and every process/LWP scheduling status.
