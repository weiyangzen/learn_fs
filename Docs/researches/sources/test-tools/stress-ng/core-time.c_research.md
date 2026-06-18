# sources/test-tools/stress-ng/core-time.c

## Purpose
`core-time.c` provides common wall-clock timestamp helpers and human-readable duration formatting.

## Important APIs, Types, And Functions
`stress_time_timeval_to_double` converts `timeval` to seconds. `stress_time_now` returns seconds as a `double`, preferring `clock_gettime(CLOCK_REALTIME)` through `stress_time_now_timespec` and falling back to `gettimeofday` through `stress_time_now_timeval` after a failure. `stress_time_duration_to_str` formats seconds into years, days, hours, minutes, and seconds using the internal `stress_format_time`.

## Control Flow
The first call path uses the current function pointer, initially the timespec implementation. If it fails, `stress_time_now` swaps the pointer to the timeval implementation and retries. Duration formatting emits only nonzero larger units, optionally forces seconds, and returns `"0 secs"` when nothing was emitted.

## State And Persistence
The only mutable state is the static function pointer `stress_time_now_func` and the static output buffer in `stress_time_duration_to_str`. No persistent data is written.

## Dependencies And Integration Points
It depends on libc time APIs, stress-ng numeric constants, attribute macros, and safe string helpers. Timing is consumed broadly by stressor loops, metrics, status output, throttling, and reports.

## Risks
`stress_time_duration_to_str` returns a static buffer and is not thread-safe across simultaneous callers. `CLOCK_REALTIME` can move with wall-clock adjustments; duration-sensitive code may prefer monotonic time but this helper intentionally reports wall time. The function-pointer fallback is global and unsynchronized.

## Test Signals
Runtime signals include stressor loop timing, metrics rates, `--status` elapsed-time output, and tests that run on systems without `clock_gettime`. Formatting issues are visible in status and YAML/log reports.
