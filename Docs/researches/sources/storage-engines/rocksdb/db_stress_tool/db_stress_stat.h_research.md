# sources/storage-engines/rocksdb/db_stress_tool/db_stress_stat.h

## Purpose

`db_stress_stat.h` defines the `Stats` accumulator used by each stress worker and by the final merged report. It tracks operation counts, read/write/delete/iteration mix, bytes written, errors, CompactFiles outcomes, optional per-operation latency histograms, progress reports, and formatted throughput output.

## Important APIs, Types, and Functions

- `Start()` resets counters and timestamps.
- `Merge()` folds another thread's counters and histogram into the receiver.
- `Stop()` records finish time and elapsed seconds.
- `FinishedSingleOp()` optionally records latency, prints long-operation notices, increments operation count, and emits progress messages.
- Counter helpers update writes, gets, prefixes, iterations, deletes, range deletes, errors, verified errors, and CompactFiles outcomes.
- `Report()` prints throughput, operation mix, error counts, CompactFiles counts, and optional histogram output under a static mutex.

## Control Flow and State Behavior

Each `ThreadState` owns a `Stats` object. Worker loops call `Start()`, update counters as operations execute, call `FinishedSingleOp()` per operation, and call `Stop()` when complete. `db_stress_driver.cc` merges worker stats into thread zero and reports them unless the run is verification-only.

`FinishedSingleOp()` measures time since the previous operation, including stress overhead and blocking. Progress output uses increasing thresholds to limit output volume. `Report()` refuses normal throughput output if there are no writes or no operations.

## Dependencies and Integration Points

The class depends on RocksDB histogram implementation, port mutexes, `SystemClock`, gflags `histogram` and `progress_reports`, and RocksDB size-format macros. It is embedded in `ThreadState`, updated by stress workload implementations, and aggregated by `db_stress_driver.cc`.

## Risks and Edge Cases

`Stats` assumes one thread mutates each instance and merge happens after workers finish. The default constructor does not initialize fields; callers must call `Start()`. `Merge()` assigns `covered_by_range_deletions_` from the other instance instead of adding it, which can underreport aggregate coverage. Read-only or verification-only workloads can hit the `No writes or ops?` guard.

## Test Signals

Useful signals are progress messages, final `Stress Test` throughput output, optional histogram output with `--histogram`, long-op notices, and plausible aggregate operation counts matching configured workload percentages.
