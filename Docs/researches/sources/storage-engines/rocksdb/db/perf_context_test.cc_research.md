# sources/storage-engines/rocksdb/db/perf_context_test.cc

## Purpose
`perf_context_test.cc` validates RocksDB's thread-local `PerfContext` counters and timers across reads, writes, iterators, mutex instrumentation, merge operations, per-level counters, CPU timers, and command-line profiling modes. It is both a correctness suite and an optional diagnostic benchmark when verbose flags are used.

## Important APIs, Types, And Functions
Global flags configure key count, random insertion, memtable type, write buffer sizes, and verbose output. `OpenDb` opens the per-thread DB with those options and optional hash skip-list memtable.

`ProfileQueries` is the central helper. It writes keys with a mid-stream flush, collects histograms from `get_perf_context()` for Put/Get/MultiGet counters and timers, optionally asserts timing counters are positive, reopens read-only, and repeats read measurements.

Tests use `SetPerfLevel`, `get_perf_context()->Reset`, `PerfContext::ToString`, per-level macros such as `PERF_COUNTER_BY_LEVEL_ADD`, `StopWatch`/`StopWatchNano`, `InstrumentedMutex`, `InstrumentedCondVar`, merge operators, snapshots, `GetEntity`, `MultiGetEntity`, iterators, and CPU-time perf levels.

## Control Flow
`SeekIntoDeletion` creates many keys, deletes all but one, then profiles `Get`, `SeekToFirst`, `Seek`, and `Next` over tombstone-heavy state. `StopWatchNanoOverhead` and `StopWatchOverhead` measure timer overhead into histograms.

`KeyComparisonCount` runs `ProfileQueries` under count-disabled/time-enabled levels, ensuring counters can be enabled, disabled, and time-validated. `SeekKeyComparison` profiles put and seek comparison counts after sequential or random insertion.

Mutex tests create instrumented locks and condition variables and verify DB mutex wait counters are populated only for DB mutex stats codes and only at relevant perf levels. `ToString` verifies zero-inclusion/exclusion formatting.

Merge tests validate both timing and counts. `MergeOperatorTime` expects merge operator time after memtable reads, flushed SST reads, and compaction. `MergeOperandCount` writes keys with increasing merge operand counts protected by snapshots, then verifies point lookup, entity lookup, MultiGet, MultiGetEntity, and forward/backward iteration counters in memtable and table-file states.

Copy/move and per-level tests verify `PerfContext` ownership semantics, enable/disable behavior, by-level aggregation, and string rendering. `CPUTimer` skips if CPU nanos are unsupported, then asserts CPU-time counters monotonically increase for Get and iterator operations. `WriteMemtableTimePerfLevel` checks write memtable time is present under wait timing but not under count-only perf level.

## State And Persistence Behavior
The file repeatedly destroys and reopens a real DB. Flushes split reads between memtable and SST paths; read-only reopen verifies counters in read-only DB mode. Snapshots in the merge-count test preserve merge operands through flush so counters reflect unresolved operands rather than collapsed state.

`PerfContext` itself is thread-local transient state. Tests reset it around each operation and assert counters reflect only the current measured call. Per-level state can be enabled, disabled, copied, moved, cleared, and rendered.

## Dependencies And Integration Points
Dependencies include public `rocksdb/perf_context.h`, DB APIs, memtable factories, merge operators, histogram and stop-watch utilities, instrumented mutex/condition variable classes, thread-status test hooks, CPU clock support, and string utilities.

Integration points span DB read/write internals, WAL writing, memtable insertion, output-file lookup, read-only open, mutex wait instrumentation, merge resolution, iterator movement, per-level Bloom/cache counters, and performance level selection.

## Risks
Timing assertions can be environment-sensitive. The suite uses `EXPECT_GT`/`ASSERT_GT` only when perf level should enable timers, but very fast operations or unsupported CPU timers require care; CPU timer tests skip when unsupported.

Global flags can make the test more expensive or alter behavior. Debug-only mutex delay hooks are guarded, so release/debug builds have different expectations for mutex wait totals. Per-level copy/move tests mutate the global thread-local context with `std::move`, so they must reset and clear state carefully.

## Test Signals
Success signals include nonzero or zero counters at the expected perf levels, correct `ToString` filtering, DB mutex wait counters only for DB mutex stats codes, positive merge operator time, exact merge operand counts for keys with 1/2/3 operands, monotonic CPU iterator timers, correct per-level string fragments, and write memtable timing only when the selected perf level records it.
