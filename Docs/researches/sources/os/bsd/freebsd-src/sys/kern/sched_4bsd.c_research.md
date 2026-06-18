# File Research: sources/os/bsd/freebsd-src/sys/kern/sched_4bsd.c

## Purpose
Implements the classic FreeBSD 4BSD scheduler as a selectable `struct sched_instance`. It provides thread priority decay, run queue management, context-switch integration, SMP wakeup forwarding, priority lending, CPU affinity handling, idle thread behavior, and scheduler statistics/probes.

## Key Elements
- `struct td_sched` extends `struct thread` with 4BSD-specific scheduling state: `%cpu`, estimated CPU, CPU ticks, sleep time, remaining slice, flags, run queue pointer, and optional KTR thread name cache.
- Scheduler flags include `TDF_DIDRUN`, `TDF_BOUND`, `TDF_SLICEEND`, `TDP_RESCHED`, and `TSF_AFFINITY`.
- Global state includes `sched_lock`, `runq`, optional per-CPU run queues, `idle_cpus_mask`, `sched_tdcnt`, `realstathz`, and `sched_slice`.
- Sysctls expose `kern.sched.4bsd.quantum`, `kern.sched.4bsd.slice`, and SMP wakeup-forwarding controls.
- `sched_4bsd_instance` fills the scheduler operation table and is registered with `DECLARE_SCHEDULER(..., "4BSD", ...)`.

## Priority and CPU Accounting
The scheduler uses the traditional 4BSD `estcpu` decay model. `schedcpu()` runs once per second in a kernel process, walks all processes/threads, decays `%cpu` and `ts_estcpu`, tracks sleep time, and recomputes timeshare priorities. `sched_clock_tick()` updates current-thread CPU usage each stat tick, recomputes priority at estimator thresholds, and requests rescheduling when the time slice expires.

Timeshare priority is computed from:
- Base `PUSER`.
- Estimated CPU divided by `INVERSE_ESTCPU_WEIGHT`.
- Nice value weighted by `NICE_WEIGHT`.

## Run Queue Model
On UP, runnable threads go to the global `runq`. On SMP, threads with pinning, binding, or restricted affinity go to per-CPU queues; other threads go to the global queue. `sched_4bsd_choose()` compares the global queue with the current CPU's per-CPU queue and returns the best runnable thread, falling back to the idle thread.

## Context Switch and Lifecycle
- `sched_4bsd_init()` initializes thread0 scheduler state and `sched_lock`.
- `sched_4bsd_setup()` initializes `ccpu`, run queues, load accounting for thread0, and the private scheduler AST.
- `sched_4bsd_sswitch()` handles switch-out accounting, requeues still-running threads, chooses the next thread, performs tracing/hooks, calls `cpu_switch()`, and restores lock/accounting state.
- `sched_4bsd_fork_thread()`, `sched_4bsd_exit_thread()`, `sched_4bsd_fork_exit()`, `sched_4bsd_throw()`, and `sched_4bsd_ap_entry()` cover thread creation, exit, first run, final switch, and AP startup.
- Constructors/destructors are not relevant here; this is runtime scheduler machinery.

## Preemption, Priority Lending, and Sleep/Wakeup
- `maybe_preempt()` requests immediate preemption when a newly runnable thread outranks the current thread and preemption policy allows it.
- `maybe_resched()` defers rescheduling through `TDP_RESCHED` and a scheduler AST.
- `sched_4bsd_lend_prio()`, `sched_4bsd_unlend_prio()`, `sched_4bsd_lend_user_prio()`, and related helpers implement priority inheritance/lending behavior.
- `sched_4bsd_sleep()` resets sleep accounting and may temporarily assign sleep priority.
- `sched_4bsd_wakeup()` updates stale priorities after long sleeps, restores interrupt-thread base priority if needed, resets the time slice, and queues the thread.

## SMP Behavior
SMP support includes per-CPU run queues, load lengths, idle CPU masks, wakeup forwarding, remote CPU kicking, and CPU selection for affinity-restricted threads. `forward_wakeup()` can wake idle CPUs through `cpu_idle_wakeup()` or IPIs; `kick_other_cpu()` sends AST or preemption IPIs when a better-priority thread lands on another CPU's queue. `sched_pickcpu()` chooses the least-loaded allowed CPU, preferring the last CPU when valid.

## Instrumentation
The file emits KTR events, SDT probes (`change-pri`, enqueue/dequeue, on/off CPU, load changes, surrender), scheduler statistics for interrupt-thread demotions/preemptions, optional HWPMC hooks, optional hardware tracing hooks, and DTrace virtual-time switch hooks.

## Filesystem / VM Relevance
The file is not filesystem-specific. It is still relevant to filesystem research because VFS, storage, page daemon, and interrupt/workqueue threads are scheduled through this implementation when 4BSD is active. Run queue latency, priority lending, and interrupt-thread demotion can directly influence filesystem and block I/O responsiveness.

## Notable Edge Cases
- `INVERSE_ESTCPU_WEIGHT` is tuned for statclock frequencies around 100-256 Hz and scales with CPU count on SMP.
- `sched_4bsd_do_timer_accounting()` avoids accounting on halted/disabled HTT CPUs for 4BSD.
- Bound threads can force a voluntary switch when bound to a different CPU.
- Affinity updates may move run-queued threads to valid per-CPU queues or force running threads off disallowed CPUs.
- `sched_4bsd_find_l2_neighbor()` is a stub returning `-1`.
