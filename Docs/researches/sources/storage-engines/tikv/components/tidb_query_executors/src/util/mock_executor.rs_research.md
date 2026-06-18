# sources/storage-engines/tikv/components/tidb_query_executors/src/util/mock_executor.rs

## Purpose

`util/mock_executor.rs` provides test-only mock implementations of batch executors, storage, and region storage accessors. It supplies deterministic fixture batches for executor unit tests and lightweight storage/accessor behavior for code paths that require storage abstractions.

## Important APIs, Types, and Functions

- `MockExecutor` implements `BatchExecutor` over a fixed iterator of `BatchExecuteResult`s, optional child executor, optional intermediate schema/results, optional scanned range, and pending scanned-row accounting.
- `MockExecutor::new`, `new_with_child`, `set_next_intermediate_results`, and `set_extra_common_handle_keys` build and mutate test fixtures.
- `MockScanExecutor` is a simple one-column integer batch source honoring `scan_rows`.
- `MockStorage` implements the `Storage` trait but leaves scan/get methods unimplemented; it primarily carries region/range data.
- `MockAccessorExpect` stores expected region lookup and local storage calls for expectation mode.
- `MockRegionStorageAccessor` supports expectation mode and data-driven mode for `RegionStorageAccessor`.

## Control Flow

`MockExecutor::next_batch` delegates to a child if present; otherwise it pops the next fixture result and increments `pending_scanned_rows` by the logical row count. Stats collection pushes pending scanned rows into `ExecuteStats.scanned_rows_per_range` and resets the counter, then delegates to any child. Intermediate schema and intermediate result consumption check local configuration first and then child configuration.

`MockScanExecutor::next_batch` emits up to `scan_rows` integer rows from its `rows` vector, building logical rows from `0..real_scan_rows` and returning drain when the position reaches the end.

`MockRegionStorageAccessor` in expectation mode consumes one preloaded expectation per method call and asserts keys or success flags. Data mode scans sorted regions to return `Found` or `NotFound` with the next region start. Local region storage returns a `MockStorage` containing the selected region and requested key ranges.

## State and Persistence Behavior

All state is process-local test state. `MockExecutor` consumes result iterators and tracks pending scanned rows until stats collection. `MockScanExecutor` advances `pos`. Expectation mode stores mutable expectations behind `Arc<Mutex<MockAccessorExpect>>`, allowing cloned accessors to share expectations. No durable persistence exists.

## Dependencies and Integration Points

The file depends on `BatchExecutor`, `BatchExecuteResult`, `ExecuteStats`, storage traits from `tidb_query_common`, `kvproto` region/range protobuf types, `EvalWarnings`, `LazyBatchColumnVec`, and TiKV region key checks. It is used by aggregation, TopN, and other executor tests to avoid real storage.

## Risks and Edge Cases

- `MockExecutor::next_batch` unwraps the next result; tests must provide enough fixture batches.
- `take_scanned_range` unwraps unless delegated to a child; callers must set `scanned_range`.
- `MockStorage` methods are unimplemented and will panic if used for real scanning.
- Expectation mode panics on missing, extra, or mismatched expectations; this is useful in tests but not a tolerant fake.
- `MockScanExecutor` calculates `real_scan_rows` as `min(scan_rows, self.rows.len())`, not remaining rows, but the loop also checks `self.pos`, so it may allocate more capacity than needed but still emits correctly.

## Test Signals

The file itself is test infrastructure and has no local test module. It is heavily exercised by executor tests in aggregation, stream aggregation, TopN, table scan-adjacent scenarios, and likely region-range tests elsewhere. The pending scanned row behavior was added to support tests that verify `max_keys_read`/execution stats semantics.
