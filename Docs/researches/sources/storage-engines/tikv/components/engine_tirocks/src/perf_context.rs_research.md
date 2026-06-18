<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/tikv/components/engine_tirocks/src/perf_context.rs -->
# sources/storage-engines/tikv/components/engine_tirocks/src/perf_context.rs

## Purpose
`perf_context.rs` implements TiKV perf-context collection for the tirocks backend. It configures RocksDB perf flags/levels, captures read/write perf counters, exports Prometheus metrics, and writes selected values into TiKV request trackers.

## Important APIs, Types, and Functions
`RocksPerfContext` implements `engine_traits::PerfContext`; `PerfContextExt for RocksEngine` constructs it. `PerfContextStatistics` stores perf level, kind, accumulated read/write contexts, and last read-metric flush time.

`ReadPerfContext` and `WritePerfContext` are derived arithmetic/KV structs for RocksDB perf fields. `PerfContextFields` and `PerfStatisticsInstant<P>` support snapshot/delta logging for read or write perf contexts.

Static metrics include raftstore apply/store write histograms and storage/coprocessor read perf counters. `DEFAULT_WRITE_PERF_FLAGS` and `DEFAULT_READ_PERF_FLAGS` define the tirocks perf counters enabled when the requested level is `Uninitialized`.

## Control Flow
`start` resets the tirocks thread-local perf context and applies settings unless perf is disabled. `apply_perf_settings` chooses default read flags for storage/coprocessor, default write flags for raftstore apply/store, or explicit perf level otherwise.

`report` branches by `PerfContextKind`. Raftstore write paths capture write perf context, observe write durations into apply/store histograms, and update tracker metrics for each token. Storage/coprocessor paths capture read perf context, report selected counters to trackers, accumulate into `self.read`, and flush Prometheus read counters every two seconds.

`maybe_flush_read_metrics` moves the accumulated read context out with `mem::take`, selects storage or coprocessor counter vec by tag, and increments a long list of labeled counters. `PerfStatisticsInstant::delta` captures current fields and subtracts the stored baseline.

## State and Persistence Behavior
Perf context state is thread-local inside tirocks/RocksDB and reset at observation start. This module accumulates read counters between flushes and mutates Prometheus counters/histograms plus tracker metrics. It does not persist storage data.

## Dependencies and Integration Points
It depends on tirocks `PerfContext`, `PerfFlags`, `PerfFlag`, `set_perf_flags`, `set_perf_level`, engine-trait perf abstractions, Prometheus/static metrics, `tracker::GLOBAL_TRACKERS`, slog KV serialization, and `util::to_rocks_perf_level`.

## Risks and Edge Cases
Perf settings are thread-local; forgetting `start_observe` or running operations on another thread yields wrong metrics. Read metric flushing is time-based, so short-lived contexts may not emit Prometheus counters promptly. The large manual label list must stay in sync with `ReadPerfContext` fields and tirocks APIs. Explicit perf levels bypass default flag selection. `PerfStatisticsInstant` is intentionally `!Send`/`!Sync` through `PhantomData<*const ()>`.

## Test Signals
Tests cover arithmetic operations on `ReadPerfContext` and direct field mutation. Additional tests should cover disabled perf, uninitialized default flag selection by kind, tracker updates, flush interval behavior, write histogram observation, and delta capture after real RocksDB operations.
<!-- END_FILE_RESEARCH: sources/storage-engines/tikv/components/engine_tirocks/src/perf_context.rs -->
