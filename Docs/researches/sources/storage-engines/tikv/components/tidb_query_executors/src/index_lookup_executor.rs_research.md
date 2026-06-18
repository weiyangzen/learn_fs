# sources/storage-engines/tikv/components/tidb_query_executors/src/index_lookup_executor.rs

## Purpose
This file implements the batch index lookup executor. It consumes index-scan results from a source executor, extracts row handles, groups table row lookups by local region, performs table scans for locally available leader regions, and returns rows from the table side while preserving unresolved index rows as intermediate results for fallback.

## Important APIs, types, and functions
`BatchIndexLookUpExecutor<S, Src, Builder, F>` is the main executor. It stores source executor state, config, output table schema, force-fallback flag, adaptive table lookup batch size, optional table task builder, table scan parameters, current phase, intermediate results, channel indices, and table scan summary. `BuildIndexLookUpExecutorOptions` carries construction inputs from planner code. `build_index_lookup_executor` rejects keep-order requests, extracts index handle offsets/types from source schema, builds `TableScanParams`, and optionally creates an `AccessorTableTaskIterBuilder`.

`IndexLookUpPhase` has `IndexScan`, `TableLookUp`, and `Done` states. `IndexScanState` buffers index batches and row count. `TableLookUpState` carries an optional table task iterator and optional active table scan executor.

`TableTaskIterBuilder` constructs a `TableTaskIterator` from buffered index results. `AccessorTableTaskIterBuilder` binds table ID, region accessor, and `IndexLayout`. `AccessorTableTaskIterator` decodes handle columns, extracts `RowHandle`s, sorts handles, finds regions, builds key ranges, tracks fallback rows, and produces `TableTask`s. `TableTask` converts storage plus raw key ranges into a `BatchTableScanExecutor`.

## Control flow
In `IndexScan` phase, `on_phase_index_scan` pulls from the source executor. It returns an empty output batch carrying source drain status or warnings while buffering non-empty index results. If `force_no_index_lookup` is active, non-empty source results go straight to `intermediate_results`, and the executor finishes when the source drains. Otherwise, once the source drains or buffered row count reaches the adaptive threshold, it doubles the threshold up to `BATCH_MAX_SIZE` and transitions to `TableLookUp`.

`step_to_table_lookup` creates an `EvalContext`, builds a table task iterator from buffered results, and merges any handle decoding warnings. In `TableLookUp`, the executor either continues an active table scan or asks the iterator for the next task. Drained table scans are released after their summary is collected, and their drain status is converted back to `Remain` because more table tasks or source batches may remain. When the iterator is exhausted, unresolved rows are appended to `intermediate_results`; the executor either loops back to `IndexScan` or enters `Done` if the source is drained.

`AccessorTableTaskIterator::new` ensures handle columns are decoded, extracts handles through `RowHandle::from_lazy_batch_column_vec`, and sorts `(result_index, logical_row_index)` by handle value. `next_task` finds the region for the next handle, scans forward while subsequent handles stay before the same region end, coalesces consecutive int handles into larger ranges, clamps range ends to region end when necessary, obtains local region storage, and advances the cursor. Failed region lookup, follower role, storage acquisition failure, or region-end decode failure mark rows as left for fallback.

## State and persistence behavior
All state is in-memory for a single executor invocation. Buffered index batches are moved between phase states and `intermediate_results`. `finish_table_task_iter` transfers unresolved rows out of the iterator. `table_scan_exec_summary` accumulates stats for inner table scans and is drained into outer `ExecuteStats`. No data is persisted; storage reads are delegated to region storage accessors and table scan executors.

## Dependencies and integration points
The executor depends on `BatchExecutor`, `BatchTableScanExecutor`, `RegionStorageAccessor`, `Storage`, `FindRegionResult`, `StateRole`, `txn_types::Key`, table codec `RowHandle`, `EvalConfig`/`EvalContext`, `LazyBatchColumnVec`, `tipb::IndexLookUp` and `TableScan`, and table scan field-type conversion helpers. It integrates with intermediate result channels so unresolved rows can be reconciled by higher-level DAG execution.

## Risks and edge cases
Keep-order is unsupported. Paging and max-keys-read force fallback because buffering complicates early-stop semantics. Missing table task builders also force fallback, currently including common-handle cases per TODO. Errors in `find_region_by_handle_index` and storage acquisition are swallowed into fallback rows rather than emitted, while storage scan errors from active table scans are returned. Range construction must compare raw keys converted to MVCC comparable keys against region ends, and incorrect end clamping could skip or over-read rows. The executor is not cacheable because it reads regions outside the source region.

## Test signals
Tests cover iterator construction and handle sorting, region/task generation, consecutive range coalescing, follower/not-found/storage-error fallback rows, exhausted iterators, table scan executor construction, index scan phase buffering and adaptive threshold growth, table lookup phase task execution and summary collection, forced fallback for paging/max-keys/missing builder, intermediate result channel behavior, intermediate schema routing, and table scan summary accounting.
