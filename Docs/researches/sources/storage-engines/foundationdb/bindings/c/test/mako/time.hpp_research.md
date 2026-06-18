# sources/storage-engines/foundationdb/bindings/c/test/mako/time.hpp

## Purpose
`time.hpp` provides lightweight chrono aliases and stopwatch utilities for Mako latency, throttling, warmup, and duration reporting.

## Important APIs, Types, and Functions
- `steady_clock`, `timepoint_t`, and `timediff_t` standardize monotonic timing.
- `toDoubleSeconds`, `toIntegerSeconds`, and `toIntegerMicroseconds` convert chrono durations for reports and counters.
- `StartAtCtor` tags immediate-start stopwatch construction.
- `Stopwatch` records start/stop timepoints, supports starting from an existing time, setting stop manually, restarting from stop, and computing `diff`.

## Control Flow
Mako creates stopwatches around whole transactions, individual operations, commits, populate runs, throttling windows, and trace intervals. The stopwatch is intentionally passive: callers must call `stop` or `setStop` before `diff`.

## State and Persistence Behavior
State is two in-process monotonic timepoints. There is no file or cluster persistence.

## Dependencies and Integration Points
It depends only on `<chrono>` and is included by stats and Mako driver code. `WorkflowStatistics::addLatency` converts stopwatch diffs to microseconds through this header.

## Risks
Default-constructed `Stopwatch` has zero-initialized timepoints, so using `diff` before start/stop is a caller bug. Integer conversions truncate fractional units. There is no overflow guard for extremely long durations converted to unsigned integer units.

## Test Signals
Simple unit tests can assert conversion behavior and stopwatch monotonicity. Integration signal comes from nonzero latencies and stable TPS throttling in Mako runs.
