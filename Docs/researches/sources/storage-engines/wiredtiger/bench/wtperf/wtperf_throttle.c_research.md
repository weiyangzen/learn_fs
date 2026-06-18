# sources/storage-engines/wiredtiger/bench/wtperf/wtperf_throttle.c

## Purpose
`wtperf_throttle.c` implements per-worker operation throttling so a workload can cap operations per second.

## Important APIs, Types, And Functions
The public functions are `setup_throttle` and `worker_throttle`. Both operate on `WTPERF_THREAD.throttle_cfg`, which stores the last refill timestamp, remaining operation count, operations per increment, and microseconds per increment.

## Control Flow
`setup_throttle` maps a configured per-thread throttle into an operation bucket. Very low rates use one operation with a larger interval, ordinary rates target `THROTTLE_OPS` operations per interval, and high rates use 100 microsecond increments with more operations per increment. The main worker loop decrements `ops_count` after each operation and calls `worker_throttle` when it reaches zero. `worker_throttle` sleeps for the remaining interval or refills proportionally when the worker is behind.

## State And Persistence Behavior
All state is per-thread and in-memory. There is no persistent output except indirect effects on benchmark throughput and monitor logs.

## Dependencies And Integration Points
It depends on time conversion macros from `wtperf.h`, WiredTiger time helpers `__wt_epoch` and `WT_TIMEDIFF_US`, and `usleep`. The `worker` loop in `wtperf.c` is the sole consumer.

## Risks
Throttle zero is handled by callers; this file assumes nonzero throttle. Integer division can make low rates coarse, and scheduler sleep granularity can dominate small intervals. Refilling based on elapsed time intentionally lets delayed workers catch up, which may create short bursts.

## Test Signals
Run workloads with throttle below 100 ops/sec, midrange rates, and high rates; compare monitor ops/sec to configured caps and verify no divide-by-zero when throttle is disabled.
