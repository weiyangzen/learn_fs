# sources/storage-engines/tikv/components/in_memory_engine/src/perf_context.rs

## Purpose

This file provides a thread-local performance context compatible with RocksDB-style read metrics. It collects per-thread byte and internal-skip counters for in-memory engine gets and iterators without forcing every hot operation through global atomics.

## Important APIs, Types, And Functions

- `PERF_CONTEXT` is a `thread_local!` `RefCell<PerfContext>`.
- `PerfContext` holds `get_read_bytes`, `iter_read_bytes`, `internal_key_skipped_count`, and `internal_delete_skipped_count`.
- `perf_counter_add!` increments a named field in the current thread's context.

## Control Flow

Read code imports `PERF_CONTEXT` and the exported macro. Point reads increment `get_read_bytes` after returning a visible value. Iterators aggregate local read bytes in `LocalStatistics`, and on drop add the iterator byte count to `iter_read_bytes`; iterator traversal also increments internal key/delete skip counters during MVCC visibility filtering.

## State And Persistence Behavior

State is per-thread and in-memory only. It is not automatically reset by this file, so callers/tests that compare deltas must account for prior operations on the same thread. The `RefCell` provides interior mutability in single-thread-local scope, not cross-thread sharing.

## Dependencies And Integration Points

The module depends only on `std::cell::RefCell`. Its macro is used heavily by `read.rs`, and `RegionCacheIterMetricsCollector` exposes selected fields through `engine_traits::IterMetricsCollector`.

## Risks And Edge Cases

Because counters are thread-local, aggregating across worker threads requires external collection logic. The macro assumes the supplied identifier is an existing `PerfContext` field, so renames are compile-time breaking changes. Tests that do not reset the context may be order-sensitive if run on the same test thread and assert absolute values.

## Test Signals

`read.rs` contains direct assertions for `get_read_bytes`, `iter_read_bytes`, and skip counters, including comparisons with RocksDB statistics in `test_read_flow_metrics` and tombstone counting in `test_tombstone_count_when_iterating`.
