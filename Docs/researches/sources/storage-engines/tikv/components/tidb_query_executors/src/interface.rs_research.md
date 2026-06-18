# sources/storage-engines/tikv/components/tidb_query_executors/src/interface.rs

## Purpose
`interface.rs` defines the common batch-executor contract used by TiKV's pushed-down SQL executor pipeline. It describes how executors expose schemas, pull batches, propagate intermediate results, collect execution and storage statistics, return scanned ranges, and report whether their output can be cached. It also defines the batch result container and the drain-state enum used by all batch executors.

## Important APIs, Types, and Functions
- `BatchExecutor`: async pull-based executor trait. It is `Send`, has an associated `StorageStats`, and is the central interface implemented by scan, limit, selection, projection, aggregation, top-n, lookup, and wrapper executors.
- `BatchExecutor::schema`: returns output `FieldType` schema.
- `intermediate_schema` and `consume_and_fill_intermediate_results`: support executor families that produce/consume intermediate results, such as aggregation or multi-stage plans.
- `next_batch(scan_rows)`: async batch pull. It may return zero logical rows while still not drained.
- `collect_exec_stats`, `peek_scanned_rows_sum`, `collect_storage_stats`, `take_scanned_range`, and `can_be_cached`: stats/range/cache hooks that parents and runners call recursively.
- `collect_summary`: wraps an executor in `WithSummaryCollector<ExecSummaryCollectorEnabled, Self>` for per-executor execution summaries.
- `WithSummaryCollector<C, T>`: transparent executor wrapper that measures `next_batch` iteration time and row count, collects summary data, and delegates all other behavior to the inner executor.
- `BatchExecuteResult`: columnar batch result with `physical_columns`, logical row offsets, warnings, and drain status.
- `BatchExecIsDrain`: `Remain`, `Drain`, and `PagingDrain`; `is_remain` and `stop` are convenience methods for loop control.
- Blanket `BatchExecutor for Box<T>`: lets dynamic executors be used through `Box<dyn BatchExecutor<...>>`.

## Control Flow
Executors are pulled by repeatedly calling `next_batch`. A returned `BatchExecuteResult` contains physical column storage plus a `logical_rows` vector that selects and orders valid row offsets. Parent executors must not infer completion from an empty logical batch; they must inspect `is_drained`. `Drain` means the executor is completely exhausted, `PagingDrain` means a paging request should stop and return a scanned range, and `Remain` means callers should continue.

Stats collection is out-of-band from batch data flow. `collect_exec_stats` and `collect_storage_stats` may be called multiple times and must drain accumulated metrics since the previous call. `WithSummaryCollector::next_batch` surrounds the inner call with `on_start_iterate`/`on_finish_iterate` and records logical row count. Its `collect_exec_stats` first collects summary data into `dest.summary_per_executor`, then asks the inner executor to collect its stats.

## State and Persistence Behavior
`BatchExecuteResult` owns each batch's data and warnings; it is `Send` but intentionally not `Sync`. `WithSummaryCollector` carries mutable summary state and an inner executor. The trait methods imply ephemeral execution state: stats and storage stats are accumulated in executor instances and reset on collection, scanned range is taken by value, and no persistence is performed here.

## Dependencies and Integration Points
- Uses `async_trait` because `BatchExecutor::next_batch` is async in a trait.
- Re-exports `ExecSummaryCollector` and `ExecuteStats` from `tidb_query_common`.
- Uses `LazyBatchColumnVec` and `EvalWarnings` from `tidb_query_datatype` for batch data and warnings.
- Uses `tipb::FieldType` as the schema representation shared with pushed-down TiDB plans.
- Used directly by `index_scan_executor.rs`, `limit_executor.rs`, and other executors exported by `lib.rs`.

## Risks and Edge Cases
- Callers must respect `logical_rows`; `physical_columns.rows_len()` can include filtered or unordered rows and is not the logical output cardinality.
- Empty batches with `Remain` are legal, so loops that stop on empty output can truncate results.
- `is_drained` is a `Result<BatchExecIsDrain>`. Error means retrieval failed and the executor should be considered drained, but the batch can still contain valid remaining data that should be processed.
- `PagingDrain` stops execution for the current request without meaning the entire underlying range is permanently exhausted.
- Implementors must recursively call stats collection on children; missed calls hide metrics.

## Test Signals
This file has no local test module, but its behavior is exercised indirectly by executor tests. `limit_executor.rs` tests empty-remain batches, errors before/at limits, drain propagation, and `BatchExecIsDrain::stop`. `index_scan_executor.rs` verifies scan executor integration with `BatchExecuteResult` layout and logical/physical columns. Test-only fields and helpers on `WithSummaryCollector` and `BatchLimitExecutor` show that wrapper identity and execution-path selection are expected to be observable in tests.
