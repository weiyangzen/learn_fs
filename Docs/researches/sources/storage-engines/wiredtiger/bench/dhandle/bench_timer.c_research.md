# sources/storage-engines/wiredtiger/bench/dhandle/bench_timer.c

## Purpose
This file implements a small timing accumulator used by the dhandle benchmark to measure operation counts and elapsed time per operation.

## Important APIs, Types, and Functions
Functions include `bench_timer_init`, `bench_timer_start`, `bench_timer_stop`, `bench_timer_add`, `bench_timer_add_to_shared`, `bench_timer_add_to_shared_2`, `bench_timer_add_from_shared`, internal `__bench_timer_format`, and `bench_timer_show_change`.

## Control Flow
Callers initialize a `BENCH_TIMER`, start it before an operation using `__wt_epoch`, stop it after the operation, and aggregate totals/counts either locally or into shared timers using WiredTiger release/acquire barriers. `bench_timer_show_change` compares a previous snapshot with a new snapshot and prints delta operation count plus formatted per-operation latency.

## State, Persistence, and Dependencies
Timer state is `name`, `total_nsec`, `count`, and `start_nsec`. There is no persistence. Dependencies include `WT_SESSION_IMPL`, `WT_BILLION/MILLION/THOUSAND`, memory barrier macros, asserts, and test utility formatting assertions.

## Integration Points, Risks, and Test Signals
It integrates with `bench_dhandle.c` through macros in `bench_timer.h`. Risks include asserts if start/stop are mispaired and no reset of `start_nsec` after stop, which means a single timer object is expected to be initialized before reuse. Signal is printed timing rows when counts advance.
