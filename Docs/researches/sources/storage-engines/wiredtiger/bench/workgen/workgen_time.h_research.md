# sources/storage-engines/wiredtiger/bench/workgen/workgen_time.h

## Purpose
`workgen_time.h` provides inline time conversion macros and `timespec` operators used by workgen scheduling, throttling, monitoring, and reporting.

## Important APIs, Types, and Functions
It defines constants for thousand/million/billion, nanosecond/microsecond/millisecond/second conversion macros, `operator<<`, `operator-`, `operator+`, comparison operators, `operator+=`, `operator-=`, `ts_add_ms`, `ts_assign`, `ts_clear`, `ts_sec`, `ts_ms`, `ts_us`, and `secs_us`.

## Control Flow
The helpers normalize common arithmetic on `timespec`: subtract with nanosecond borrow, add whole seconds, add milliseconds with carry, compare by seconds then nanoseconds, and convert to scalar durations. Workgen uses these functions to compute run deadlines, report intervals, throttle divisions, synchronized sleep deadlines, and elapsed times.

## State and Persistence Behavior
The file has no state and performs no persistence. All behavior is inline computation on caller-provided values.

## Dependencies and Integration Points
It requires `timespec` and C++ streams to be visible in the including translation unit. It is included by `workgen_int.h` and indirectly used throughout `workgen.cpp`.

## Risks and Edge Cases
The conversion macros do not guard overflow. `ts_add_ms` loops while `tv_nsec > NSEC_PER_SEC`; equality to exactly `NSEC_PER_SEC` is not normalized, which can leave an invalid `timespec` boundary value. `operator+(timespec,int)` only handles whole seconds. `secs_us(double)` truncates fractional microseconds through `uint64_t` return conversion.

## Test Signals
Unit tests should exercise subtraction borrow, millisecond carry including exact one-second boundaries, comparisons, zero handling, and fractional second conversion. Throttle and synchronized sleep tests indirectly validate the helpers.
