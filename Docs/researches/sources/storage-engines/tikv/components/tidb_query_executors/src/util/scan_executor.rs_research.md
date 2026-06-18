# sources/storage-engines/tikv/components/tidb_query_executors/src/util/scan_executor.rs

## Purpose

`util/scan_executor.rs` implements the generic scanning wrapper shared by table and index scan executors. It owns range scanning, batching, drain/error semantics, scanned work metrics, execution stats forwarding, storage stats forwarding, and small schema utilities.

## Important APIs, Types, and Functions

- `ScanExecutorImpl` is the strategy trait for scan-specific row materialization. Implementors provide schema, mutable eval context, column vector construction, and `process_kv_pair`.
- `ScanExecutor<S, I, F>` wraps a `RangesScanner<S, F>`, a concrete scan implementation, an executor name, and an ended flag.
- `ScanExecutorOptions` carries storage, key ranges, direction, key-only mode, point range acceptance, range-awareness, and commit timestamp loading.
- `ScanExecutor::new` validates table ranges, reverses range order for backward scans, converts protobuf ranges to storage `Range`s, and constructs `RangesScanner`.
- `fill_column_vec` pulls up to `scan_rows` KV entries, calls `process_kv_pair`, records scanned KV byte work, and normalizes columns on materialization errors.
- `field_type_from_column_info` converts `ColumnInfo` into `FieldType`.
- `check_columns_info_supported` validates primary-key handle types.

## Control Flow

`next_batch` asserts the executor has not ended and `scan_rows > 0`, asks the implementation for an empty column vector, and calls `fill_column_vec`. `fill_column_vec` loops until it has attempted `scan_rows` entries or the scanner drains. It calls `scanner.next_opt(i == scan_rows - 1)`, accumulates key/value byte sizes, and sends each KV entry to the concrete implementation. Storage errors return immediately after recording any work already done. Materialization errors truncate columns into equal length before returning the error. Drain returns `Ok(true)`, and a full batch returns `Ok(false)`.

Back in `next_batch`, columns are asserted equal length, logical rows are `0..rows_len`, and `is_drained` is translated to `Drain`, `Remain`, or error. Errors and full drain set `is_ended`; remain does not. Warnings are taken from the implementation context.

Stats methods collect scanned rows per range, peek scanned row sums, collect storage stats, return scanned ranges, and report cacheability through `RangesScanner`.

## State and Persistence Behavior

Scan progress is held in `RangesScanner`; `is_ended` is only an assertion/safety guard. The scan implementation owns its decoding context and reusable buffers. Scanned work metrics are emitted per batch through `record_executor_work`. There is no durable persistence.

## Dependencies and Integration Points

The module depends on API-version `KvFormat`, `RangesScanner`, `Storage`, protobuf `KeyRange`, `IntervalRange`, `Range`, `EvalContext`, `LazyBatchColumnVec`, `ColumnInfo`, `FieldType`, and `TimeStamp`. It is integrated by table scan and index scan implementations via `ScanExecutorImpl`.

## Risks and Edge Cases

- A TODO notes that if an error occurs after successfully retrieving rows, downstream operators such as TopN/Limit may consume only part of the rows and might need to ignore the error; current behavior returns rows plus error in `is_drained`.
- Concrete `process_kv_pair` implementations may partially fill columns before error. The wrapper truncates to equal length but cannot restore semantic row data.
- Backward scans reverse range order and configure backward in-range scanning; range conversion correctness is essential.
- Work metrics use key+value bytes and saturating addition.
- `intermediate_schema` always errors because scan executors have no child intermediate schema until root.

## Test Signals

Direct tests are in concrete scan modules such as table scan. Table scan tests exercise generic scan batching, drain states, corrupted row truncation, locked storage errors, scanned-row execution summaries, and storage range behavior through this wrapper.
