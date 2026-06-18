# sources/test-tools/stress-ng/stress-time-warp.c

## Purpose
Implements the `time-warp` stressor, which repeatedly samples all available clock/time sources and detects clocks moving backwards or wrapping below their initial value. It distinguishes monotonic clocks, where any backward step is a verification failure, from wall-clock or CPU-time sources where backward movement is counted but only final wraparound below the starting point fails.

## Important APIs, Types, And Functions
`stress_time_warp_info_t` describes each source: getter function, clock id, name, and monotonic flag. `stress_time_t` stores initial and previous timestamps plus warp and failure counters. Wrapper getters adapt `gettimeofday()`, `time()`, and `getrusage()` to a `clock_gettime`-like signature. The `clocks[]` table conditionally includes `CLOCK_REALTIME`, coarse realtime, monotonic variants, boottime, CPU clocks, TAI, auxiliary clocks, plus libc time APIs. `stress_time_warp_timespec_fix()` normalizes nanoseconds, and `stress_time_warp_lt()` compares two `timespec` values.

## Control Flow
After synchronization, the stressor samples every configured clock into `ts_init` and `ts_prev`, marking a source failed only for unexpected errors other than unsupported-clock style errno values. The main loop reads every non-failed source, increments that source's `warped` count if the new value is less than the previous value, updates `ts_prev`, and increments bogo ops. On exit it checks that each final `ts_prev` is not below `ts_init`, then checks that all monotonic sources had zero backward steps.

## State And Persistence Behavior
All state lives in a stack array for the worker invocation. No files, timers, or persistent system state are created. The stressor is read-only against kernel timekeeping APIs.

## Dependencies And Integration Points
The implemented path needs at least one of `clock_gettime` with librt, `gettimeofday`, `time`, or `getrusage`. It uses stress-ng clock shims, synchronization, proc-state, and bogo helpers. Metadata registers `CLASS_OS` with `VERIFY_ALWAYS`; unsupported builds export an unimplemented reason.

## Risks And Test Signals
Realtime clocks can legitimately move backwards because of administrator or NTP changes, so monotonic status is encoded per clock. `getrusage()` is represented as combined process CPU time and may not advance while idle. The comparison function normalizes out-of-range nanoseconds before testing, reducing false positives from wrapper calculations. Test signals are failure logs naming the specific clock, bogo progress from repeated reads, wraparound/warp counts at failure, and clean skip of clocks returning `EINVAL`, `ENOSYS`, or `ENODEV`.
