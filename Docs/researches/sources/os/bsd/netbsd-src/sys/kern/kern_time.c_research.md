# File Research: sources/os/bsd/netbsd-src/sys/kern/kern_time.c

## Scope

- Source file read completely: `sources/os/bsd/netbsd-src/sys/kern/kern_time.c`.
- Subset scope: `Docs/research_subset_a.md`.
- This file implements time-related syscalls, time setting, nanosleep, BSD interval timers, POSIX timers, virtual/profiling timers, and timer signal delivery.

## Purpose And Main Interfaces

- Initializes timer subsystem with `time_init`.
- Provides clock syscalls:
  - `sys___clock_gettime50`
  - `sys___clock_settime50`
  - `sys___clock_getres50`
  - `sys_clock_nanosleep`
  - `sys_clock_getcpuclockid2`
- Provides legacy time syscalls:
  - `sys___gettimeofday50`
  - `sys___settimeofday50`
  - `sys___adjtime50`
  - `sys___getitimer50`
  - `sys___setitimer50`
- Provides POSIX timer syscalls:
  - `sys_timer_create`
  - `sys_timer_delete`
  - `sys___timer_settime50`
  - `sys___timer_gettime50`
  - `sys_timer_getoverrun`
- Exports helper APIs for process timer cleanup and ticks:
  - `ptimers_free`
  - `ptimer_tick`

## Key Data Structures

- `itimer_mutex` protects interval timer state.
- `struct itimer` is the generic timer representation used for realtime, monotonic, virtual, and profiling timers.
- Realtime/monotonic timers use callouts and absolute deadlines.
- Virtual/profiling timers use per-process delta lists.
- `struct ptimers` stores the per-process timer array and virtual/prof lists.
- `struct ptimer` wraps an `itimer` with signal event state, owning process, overrun counters, timer index, and softint queue flag.
- `ptimer_queue` collects fired process timers for softint signal delivery.

## Control Flow

- `settime1` validates the target time, authorizes privileged time changes, calls `tc_setclock`, updates the RTC with `resettodr`, and notifies realtime timers.
- `clock_settime1` only allows setting `CLOCK_REALTIME`; monotonic is read-only.
- `clock_getres1` reports timecounter-derived resolution for realtime, monotonic, process CPU, and thread CPU clocks.
- `nanosleep1` converts requested time to ticks, sleeps with `kpause`, recomputes remaining time, and retries if woke early without an error.
- `adjtime1` reads or sets `time_adjtime` under `timecounter_lock`, saturating extreme deltas.
- `itimer_init`, `itimer_poison`, `itimer_fini`, `itimer_settime`, and `itimer_gettime` implement the generic interval timer lifecycle.
- `itimer_callout` fires realtime/monotonic timers, computes overruns, and rearms periodic timers.
- `timer_create1` allocates a POSIX timer slot, validates `sigevent`, initializes the right clock type, and assigns defaults when no event is supplied.
- `dotimer_settime` validates and converts absolute/relative values, then arms the generic timer.
- `dosetitimer` lazily allocates the BSD timers and maps timer kinds to signals.
- `ptimer_tick` decrements virtual/prof timers from hardclock.
- `ptimer_intr` drains the softint queue and posts `SI_TIMER` signals, compressing signals when one is already pending.

## Concurrency And Invariants

- `itimer_lock`/`itimer_unlock` wrap `itimer_mutex`.
- `itimer_fini` intentionally releases `itimer_mutex` before destroying callouts.
- `itimer_settime` can return `ERESTART` when a real timer callout fired and lock dropping may invalidate looked-up state.
- Virtual timer lists are delta-encoded; insert/remove adjusts neighboring timers.
- Process signal delivery takes `proc_lock` and drops/reacquires `itimer_mutex` around `kpsignal`.

## Risks And Edge Cases

- `time_wraps` protects against extreme time setting and negative deltas.
- Realtime timer deadlines must be updated when wall clock time changes.
- Real timer callout delays compress multiple expirations into one signal while recording overrun counts.
- POSIX timers are bounded by `TIMER_MAX`; BSD timers occupy low reserved slots.
- `SIGEV_NONE` and non-signal notifications do not enqueue signals.
