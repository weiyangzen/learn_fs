# sources/test-tools/stress-ng/stress-timer.c

## Purpose
Implements the `timer` stressor, a POSIX timer signal workload that creates a `CLOCK_REALTIME` timer, drives it at a configured frequency, optionally randomizes the interval, counts timer signal bogo events, and verifies timer API behavior around overruns and settime failures.

## Important APIs, Types, And Functions
Global state includes `s_args`, `timerid`, `timer_settime_failure`, `timer_overruns`, `rate_ns`, `time_end`, and `timer_rand`. Options are `timer-freq` and `timer-rand`. `stress_timer_set()` converts the selected frequency into a nonzero `itimerspec`, adding +/-12.5 percent jitter when random mode is enabled. `stress_proc_self_timer_read()` exercises Linux `/proc/self/timers`. `stress_timer_handler()` is the `SIGRTMIN` handler that increments bogo ops, samples overruns with `timer_getoverrun()`, periodically checks timeout and `/proc/self/timers`, and cancels the timer on shutdown.

## Control Flow
`stress_timer()` masks `SIGINT`, resolves frequency with maximize/minimize handling, installs the realtime signal handler, creates a POSIX timer, synchronizes, starts the timer, and then sleeps in 10 ms chunks. Every 1024 parent loop iterations it deliberately calls `nanosleep()` with invalid timespec values and, in random mode, stops and re-arms the timer with a newly randomized interval. When the global continue flag clears, it disarms and deletes the timer, reports overruns in debug output, fails if any settime call failed, and on Linux reissues `timer_delete()` against the already deleted id to exercise that error path.

## State And Persistence Behavior
State is process-global because signal handlers need fast access to the active args and timer id. The only kernel object is a POSIX timer, deleted before exit. No files are created; `/proc/self/timers` is read opportunistically on Linux.

## Dependencies And Integration Points
The implemented path requires librt and `timer_create`, `timer_delete`, `timer_getoverrun`, and `timer_settime`. It integrates with stress-ng option parsing, signal wrappers, proc-state, bogo accounting, timing helpers, and metrics. It registers as `CLASS_SIGNAL | CLASS_INTERRUPT | CLASS_OS` with `VERIFY_ALWAYS`.

## Risks And Test Signals
Very high configured frequencies can produce overruns, signal pressure, or resource failures; `EAGAIN`, `ENOMEM`, and `ENOTSUP` during creation become no-resource skips. Handler work is intentionally small but still calls timer APIs and stress-ng accounting, so signal-safety and errno restoration matter. Test signals include bogo events, overrun debug counts, absence of `timer_settime_failure`, graceful resource skips, and correct handling of `timer-rand` re-arming.
