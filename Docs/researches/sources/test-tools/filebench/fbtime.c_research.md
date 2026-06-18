## sources/test-tools/filebench/fbtime.c

### Purpose
`fbtime.c` supplies a portable fallback implementation of Solaris-style `gethrtime()` when the platform does not provide it. Filebench uses high-resolution nanosecond timestamps for event generation, flowop timing, and reporting.

### Important APIs, Types, And Functions
The only implemented function is `gethrtime(void)` under `#ifndef HAVE_GETHRTIME`. It returns `hrtime_t`, defined in `fbtime.h` for fallback builds.

### Control Flow
The fallback calls `gettimeofday`, multiplies seconds by one billion, converts microseconds to nanoseconds, adds them, and returns the result. If the platform already has `gethrtime`, this file contributes no replacement function.

### State And Persistence
The function is stateless and writes no persistent data. It returns wall-clock-derived time rather than a monotonic clock in fallback mode.

### Dependencies And Integration Points
It includes `sys/time.h`, `stdlib.h`, `stdio.h`, `fbtime.h`, `config.h`, and `filebench.h`. `eventgen.c` and `fileset.c` call `gethrtime` for elapsed-time calculations.

### Risks
`gettimeofday` can move backward or jump with system clock adjustments, unlike a monotonic high-resolution timer. There is no error handling for `gettimeofday` failure. Precision is microsecond-derived even though the return unit is nanoseconds.

### Test Signals
Tests should verify increasing values under normal conditions, approximate unit conversion, compilation with and without `HAVE_GETHRTIME`, and tolerance in callers for non-monotonic fallback behavior.
