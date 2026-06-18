# sources/storage-engines/wiredtiger/test/cppsuite/src/util/execution_timer.cpp

## Purpose
Implements aggregation of operation timing samples into a metrics writer statistic.

## Important APIs, Types, And Functions
`execution_timer::execution_timer` stores metric id and test name. `append_stats` sorts recorded nanosecond timings and records the 90th percentile as `<id>_nanoseconds_90th_percentile`. The destructor appends stats when samples exist.

## Control Flow
The templated `track` method in the header records samples. The `.cpp` destructor emits metrics at object lifetime end, typically when a custom operation exits.

## State And Persistence Behavior
Stores timing samples in memory. Persists only through `metrics_writer::instance().add_stat`, later emitted by the test harness perf output.

## Dependencies And Integration Points
Depends on `<algorithm>`, `<cmath>`, `execution_timer.h`, and `metrics_writer`. Used by API timing and bounded cursor performance tests.

## Risks And Test Signals
`append_stats` indexes `floor(size * 0.9)` after sorting; it is guarded by destructor sample-count check but direct callers should avoid empty data. `_test_name` is stored but not used in this implementation. The metric reflects percentile latency, not average despite the class comment.
