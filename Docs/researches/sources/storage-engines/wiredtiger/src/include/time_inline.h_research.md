# sources/storage-engines/wiredtiger/src/include/time_inline.h

Purpose: `time_inline.h` provides fast internal time helpers for wall-clock time, CPU tick reads, operation timeouts, and elapsed-time measurement.

Important APIs: `__wt_rdtsc` reads x86 `rdtsc`, ARM virtual counter `cntvct_el0`, MSVC `__rdtsc`, or returns zero on unsupported platforms. `__wt_epoch` wraps raw epoch time and enforces per-session monotonicity through `__time_check_monotonic`. `__wt_clock` chooses epoch nanoseconds or CPU ticks based on process configuration. Helpers return milliseconds/seconds, convert clock deltas to nanoseconds, start/stop/check operation timers, evaluate timers in milliseconds, and convert microseconds to `timespec`.

Control flow: callers choose raw elapsed timing through `__wt_clock` or wall-clock time through `__wt_epoch`. If a session observes time moving backward, the helper increments the `time_travel` stat and reuses the last per-session epoch value. Operation timers copy the active transaction timeout into session fields, then compare `WT_CLOCKDIFF_US(now, start)` against the configured timeout.

State and persistence behavior: state is per-session timing state (`last_epoch`, `operation_start_us`, `operation_timeout_us`) plus process-level timing configuration (`use_epochtime`, `tsc_nsec_ratio`). Nothing is persisted. The monotonicity guarantee is per session only; multiple sessions can still observe non-monotonic ordering relative to each other.

Dependencies and integration points: depends on `wt_internal.h`, stat macros, transaction flags, process timing calibration, raw epoch functions, and WiredTiger time arithmetic macros. It is used by cursor/session operations, operation timeout enforcement, perf histogram accounting, checkpoint/eviction timing, and diagnostic duration reporting.

Risks: unsupported hardware tick reads return zero, so builds must configure epoch timing or avoid interpreting raw ticks as real time. TSC conversion depends on a valid `tsc_nsec_ratio`; CPU frequency changes or unstable counters can skew elapsed results. `__wt_seconds32` has a documented 2038 limitation. Operation timeout checks only fire for running transactions and can miss non-transactional work.

Test signals: monotonic-time tests using mocked backward raw time, operation timeout tests for running and non-running transactions, platform build tests for x86/ARM/MSVC/fallback branches, perf histogram sanity checks, and tests that force epoch timing to validate nanosecond/millisecond conversions.
