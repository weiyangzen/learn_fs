# File Research: sources/os/bsd/netbsd-src/sys/kern/kern_timeout.c

## Scope

- Source file read completely: `sources/os/bsd/netbsd-src/sys/kern/kern_timeout.c`.
- Subset scope: `Docs/research_subset_a.md`.
- This file implements NetBSD callouts with per-CPU hierarchical timing wheels and soft interrupt execution.

## Purpose And Main Interfaces

- Startup and per-CPU initialization:
  - `callout_startup`
  - `callout_init_cpu`
- Callout lifecycle:
  - `callout_init`
  - `callout_destroy`
  - `callout_setfunc`
  - `callout_reset`
  - `callout_schedule`
  - `callout_stop`
  - `callout_halt`
- Callout status:
  - `callout_expired`
  - `callout_active`
  - `callout_pending`
  - `callout_invoking`
  - `callout_ack`
- Tick/dispatch:
  - `callout_hardclock`
  - internal `callout_softclock`
- DDB support:
  - `db_show_callout`

## Key Data Structures

- `struct callout_cpu` contains:
  - per-CPU lock
  - sleep queue for halt waiters
  - tick count
  - active callout and active LWP
  - late/block event counters
  - todo queue
  - 1024 timing wheel buckets
  - CPU identity
- Timing wheel constants define four 256-bucket levels.
- Circular queue macros implement intrusive queue insert, remove, append, and traversal.
- `callout_impl_t` is the private implementation stored inside public `callout_t`.
- `callout_syncobj` defines sleep behavior for threads waiting on active callouts.

## Control Flow

- `callout_startup` initializes the boot CPU callout state early enough for registration.
- `callout_init_cpu` allocates or finalizes per-CPU callout state, establishes the shared softclock softint on the boot CPU, initializes sleep queues, and attaches event counters.
- `callout_init` chooses the current CPU for MPSAFE callouts when possible; otherwise binds to CPU0.
- `callout_schedule_locked` computes absolute expiration ticks, handles rescheduling, may migrate unbound callouts to the current CPU, and queues them on `cc_todo`.
- `callout_stop` removes pending callouts and clears pending/fired state without waiting for already-running callbacks.
- `callout_halt` cancels pending work and waits if the callout is active on another LWP.
- `callout_wait` sleeps on the per-CPU callout sleep queue, optionally drops/reacquires an interlock, and repeats because callouts may reschedule themselves.
- `callout_hardclock` advances ticks, cascades timing wheel buckets into the todo queue, and schedules softclock when work exists.
- `callout_softclock` drains due callouts, re-buckets future callouts, marks due callouts fired/invoking, runs callbacks with or without kernel lock based on `CALLOUT_MPSAFE`, and wakes halt waiters after callback completion.

## Concurrency And Invariants

- Each `callout_cpu` has its own spin mutex.
- `callout_lock` loops until it locks the same CPU that still owns the callout, handling concurrent migration.
- `cc_active` plus `cc_lwp` identify in-flight callbacks.
- `callout_destroy` asserts the callout is neither pending nor running elsewhere.
- `callout_halt` is forbidden from hard interrupt context.
- Non-MPSAFE callbacks run under the kernel lock.

## Risks And Edge Cases

- Tick comparisons intentionally use unsigned arithmetic cast through signed deltas to handle wraparound.
- Re-scheduling an already-pending callout earlier moves it to `todo`; later schedules leave it in place for later reclassification.
- Halt can return with `expired=true` if it had to wait for an active callback.
- DDB inspection avoids locking because other CPUs may be paused while holding callout locks.
