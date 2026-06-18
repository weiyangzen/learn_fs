# sources/storage-engines/tikv/src/storage/mvcc/metrics.rs

## Purpose

This file centralizes Prometheus metric definitions for MVCC transaction conflict paths, duplicate command handling, check-txn-status outcomes, prewrite assertion behavior, post-commit retry detection, scan-lock read-lock hold time, and MVCC/GC version histograms. It contains no business logic; it defines stable metric names and static label enums used by MVCC readers and transaction commands.

## Important APIs, Types, and Functions

- `MvccConflictKind` labels conflict counters for prewrite conflicts, rollback observations, commit lock misses, rollback-after-commit, pessimistic lock conflicts, and pipelined pessimistic amend results.
- `MvccDuplicateCommandKind` labels duplicate command counters for prewrite, commit, rollback, and pessimistic lock acquisition variants.
- `MvccCheckTxnStatusKind` labels check-txn-status result categories: rollback, timestamp update, commit-info lookup, and pessimistic rollback.
- `MvccPrewriteAssertionPerfKind` describes whether prewrite assertions loaded writes, reloaded non-data/write-not-loaded versions, or skipped reloads.
- `ScanLockReadTimeSource` is used by `MvccReader::load_in_memory_pessimistic_lock_range` to distinguish resolve-lock and pessimistic-rollback scan-lock timing.
- `MVCC_VERSIONS_HISTOGRAM` and `GC_DELETE_VERSIONS_HISTOGRAM` are dynamic histograms keyed by `key_mode`.
- `MVCC_CONFLICT_COUNTER`, `MVCC_DUPLICATE_CMD_COUNTER_VEC`, `MVCC_CHECK_TXN_STATUS_COUNTER_VEC`, `MVCC_PREWRITE_ASSERTION_PERF_COUNTER_VEC`, `MVCC_PREWRITE_REQUEST_AFTER_COMMIT_COUNTER_VEC`, and `SCAN_LOCK_READ_TIME_VEC` are lazy static metric handles.

## Control Flow

There is no runtime control flow beyond `lazy_static!` initialization. At first use, each metric is registered in the global Prometheus registry. Static metric macros generate typed accessors so call sites use enum variants instead of ad hoc label strings. Histogram buckets use exponential series: MVCC version histograms start at 1 and double for 30 buckets; scan-lock read duration starts at 10 microseconds and doubles for 20 buckets.

## State and Persistence Behavior

All state is process-local metric state held by the Prometheus registry. Counters and histograms are monotonic or cumulative for process lifetime and are not persisted by this file. Metric samples become externally visible through TiKV's metrics exposition path.

## Dependencies and Integration Points

The file depends on `prometheus`, `prometheus_static_metric`, and `lazy_static`. `mvcc/mod.rs` re-exports `GC_DELETE_VERSIONS_HISTOGRAM` and `MVCC_VERSIONS_HISTOGRAM`. Other MVCC transaction modules increment the conflict, duplicate, check-status, assertion, and request-after-commit counters. `reader/reader.rs` imports `SCAN_LOCK_READ_TIME_VEC` and `ScanLockReadTimeSource` to observe time spent holding the in-memory pessimistic-lock table read guard.

## Risks and Edge Cases

- Registration uses `.unwrap()`, so duplicate metric registration at process initialization would panic. This is normal for TiKV statics but important for tests that isolate registries poorly.
- Label sets are fixed at compile time. New MVCC behaviors need corresponding enum additions or they will be folded into existing labels elsewhere.
- The metric description for `MVCC_PREWRITE_REQUEST_AFTER_COMMIT_COUNTER_VEC` contains a spelling typo in `TxnStatucCache`; this is cosmetic but part of exported metadata.
- Histograms with broad exponential buckets are stable but coarse at high values.

## Test Signals

This file has no local tests. Coverage is indirect through compilation of generated static metric accessors and runtime use in transaction/reader tests that touch scan-lock and MVCC paths.
