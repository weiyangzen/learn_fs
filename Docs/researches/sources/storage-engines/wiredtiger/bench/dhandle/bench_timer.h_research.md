# sources/storage-engines/wiredtiger/bench/dhandle/bench_timer.h

## Purpose
This header declares the `BENCH_TIMER` struct, timing functions, and convenience macros for measuring single and cumulative benchmark operations.

## Important APIs, Types, and Functions
`BENCH_TIMER` stores `name`, `total_nsec`, `count`, and `start_nsec`. Macros `BENCH_TIME_SINGLE` and `BENCH_TIME_CUMULATIVE` wrap statements with timer start/stop and aggregation.

## Control Flow, State, and Dependencies
Callers include the header, allocate timers, and use macros around WiredTiger operations. The cumulative macro creates a stack timer then adds its result to a shared timer. Dependencies are `WT_SESSION`, `uint64_t`, and the implementation in `bench_timer.c`.

## Integration Points, Risks, and Test Signals
The header is tightly coupled to the dhandle benchmark and WiredTiger timing/barrier primitives. Risk is macro statement side effects and required semicolon/block discipline. Signal is successful compilation and consistent operation counts in benchmark output.
