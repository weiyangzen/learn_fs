# File Research: sources/os/bsd/freebsd-src/sys/kern/kern_timeout.c

## Purpose
Implements FreeBSD's callout/timer facility: per-CPU hashed timing wheels, softclock kernel threads, direct hardclock-context callouts, scheduling, cancellation, draining, migration, precision coalescing, and callout diagnostics.

## Key Interfaces
- `callout_process()` scans the current CPU callwheel from hardclock/eventtimer context, runs direct callouts, queues soft callouts, and arms the next event.
- `softclock_thread()` drains each CPU's expire queue in the software clock thread.
- `callout_reset_sbt_on()` schedules or reschedules a callout with sbintime precision and optional CPU selection.
- `callout_schedule_on()` and `callout_schedule()` reschedule an existing callout using its stored function and argument.
- `_callout_stop_safe()` implements stop and drain semantics, including sleepqueue-based waits for in-flight callouts.
- `callout_when()` converts relative/absolute callout arguments into absolute sbintime deadlines and precision.
- `callout_init()` and `_callout_init_lock()` initialize lockless, Giant-backed, or caller-lock-protected callouts.
- `kern.callout_stat` and DDB `show callout` / `show callout_last` expose callout state.

## State And Locking
Each CPU has a `struct callout_cpu` with a spin mutex, callwheel buckets, an expire queue, the next event time, scan state, and two execution entities: one for softclock thread context and one for direct execution. Each execution entity tracks the current callout, last function/argument, cancellation and drain wait flags, and SMP deferred-migration metadata. Callouts carry target CPU, lock object, function/argument, deadline, precision, public active state, and internal pending/processed/direct/migration flags.

## Control Flow
Boot initialization sizes the callwheel from `kern.ncallout`, allocates per-CPU wheels, and later creates one `clock` kthread per CPU. `callout_process()` computes a lookahead window, scans wheel buckets, executes expired direct callouts immediately, moves other expired callouts to `cc_expireq`, updates `cc_firstevent`, and wakes the per-CPU softclock thread. `softclock_call_cc()` removes pending state, optionally acquires the callout's lock or tries it, runs the handler under no-sleep assertions and SDT/KTR probes, unlocks as required, wakes drainers, and applies deferred migration or cancellation. Scheduling removes prior pending instances, handles in-flight reschedule and SMP migration cases, reinserts the callout into the right bucket, and notifies the eventtimer if the new deadline is earlier.

## Integration Notes
The implementation integrates with eventtimers via `cpu_new_callout()`, scheduler and kthread code, KTR and SDT probes, random entropy harvesting, WITNESS/lock classes, sleepqueues, Giant, SMP CPU sets, and optional profiling and DDB support. `C_DIRECT_EXEC` callouts are constrained to spinlock-compatible locking because they can run from hardware interrupt context.

## Risks
This file is a delicate state machine. Correctness depends on preserving pending/processed/active flags while moving entries between list and tailq storage, coordinating `cc_exec_cancel` with lock acquisition, waking sleepqueue drainers without lock-order reversals, and not losing deferred migrations. Timer coalescing and callwheel wrap logic affect latency and eventtimer rearming, so changes can cause missed or late callouts. Direct callouts are especially risky because they execute outside the softclock thread.
