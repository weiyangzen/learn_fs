# sources/test-tools/stress-ng/stress-itimer.c

Purpose: implements `itimer`, an interval-timer stressor that drives high-frequency `SIGPROF` delivery via `setitimer()` and continuously samples all available interval timer types.

Important APIs/types/functions: global `s_args`, `rate_us`, and `time_end` are shared with the signal handler. `stress_itimer_set()` computes nonzero interval values, with optional random frequency jitter. `stress_itimer_handler()` increments bogo ops, checks timeout periodically, and cancels the profiling timer when stopping.

Control flow: the worker blocks `SIGINT`, selects `itimer-freq` with maximize/minimize overrides, installs a `SIGPROF` handler, sync-starts, programs `ITIMER_PROF`, and loops over `getitimer()` for all compiled `ITIMER_REAL`, `ITIMER_VIRTUAL`, and `ITIMER_PROF` entries until the stress framework stops. It reports failure if no SIGPROF signals were handled, then cancels the timer.

State and persistence behavior: state is process-local signal/timer state plus global counters. No filesystem persistence exists. The timer is explicitly disabled at shutdown and in the handler cancellation path.

Dependencies and integration points: requires `getitimer()` and `setitimer()`. Uses stress-ng settings, signal helpers, timing, bogo accounting, and process state transitions. Registered as `CLASS_INTERRUPT | CLASS_OS` with always-on verification.

Risks: very high requested frequencies are limited by kernel timer resolution and scheduling. Signal-handler work must remain async-signal safe enough for stress-ng expectations. Only `ITIMER_PROF` is actively programmed even though all available timers are queried.

Test signals: run default, minimized, maximized, and `--itimer-rand`; confirm bogo ops increase, timers are cancelled, and unsupported `ITIMER_PROF` returns `EXIT_NOT_IMPLEMENTED` rather than failure.
