# sources/storage-engines/wiredtiger/test/cppsuite/src/util/instruction_counter.cpp

## Purpose
Implements setup and metric emission for Linux hardware instruction counting.

## Important APIs, Types, And Functions
Constructor initializes `perf_event_attr` for `PERF_TYPE_HARDWARE` and `PERF_COUNT_HW_INSTRUCTIONS`, excluding kernel and hypervisor counts. `append_stats` records `<id>_instructions`. Destructor always appends the last captured count.

## Control Flow
Actual counting happens in the header's templated `track`. The `.cpp` sets static perf configuration and sends the final value to `metrics_writer`.

## State And Persistence Behavior
Stores one instruction count in `_instruction_count`. Persists a metric through `metrics_writer`.

## Dependencies And Integration Points
Depends on Linux perf event headers through the header, `instruction_counter.h`, and `metrics_writer`. Used by `api_instruction_count_benchmarks.cpp`.

## Risks And Test Signals
The utility requires Linux perf permissions; `perf_event_open` failure asserts in `track`. Only the most recent tracked lambda is retained, so one counter object is intended for one measured operation in these tests.
