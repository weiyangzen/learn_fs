# sources/storage-engines/tikv/components/tidb_query_executors/src/slow_hash_aggr_executor.rs

## Purpose

`slow_hash_aggr_executor.rs` implements `BatchSlowHashAggregationExecutor`, a grouped hash aggregation executor for batch coprocessor execution. It supports multiple GROUP BY expressions by serializing group keys into a backing byte buffer and using unsafe references into that buffer as `HashMap` keys. The file explicitly labels the approach as slow and notes a correctness caveat: serialized data is not always a fully correct group key representation, referencing TiDB issue `pingcap/tidb#10467`.

## Important APIs, Types, and Functions

- `BatchSlowHashAggregationExecutor<Src>` is a thin wrapper around the shared `AggregationExecutor<Src, SlowHashAggregationImpl>`. It forwards `BatchExecutor` methods such as `schema`, `next_batch`, stats collection, scanned range, storage stats, and cacheability to the shared executor.
- `BatchSlowHashAggregationExecutor::check_supported` requires at least one group-by expression, validates each group-by expression with `RpnExpressionBuilder::check_expr_tree_supported`, and validates aggregate functions with `AllAggrDefinitionParser`.
- `BatchSlowHashAggregationExecutor::new` builds RPN group-by expressions from protobuf `Expr` descriptors using the source schema length, then calls `new_impl`.
- `new_impl` prepares group-key bookkeeping: a leading zero in `group_key_offsets`, the list of byte-typed group-by columns that need duplicate original encoding for output, the `original_group_by_col_index` remap, and buffers/caches sized for batch processing.
- `SlowHashAggregationImpl` is the concrete `AggregationExecutorImpl`. Its main state is `states`, `groups`, `group_key_buffer`, `group_key_offsets`, `states_offset_each_logical_row`, `group_by_results_unsafe`, and `cached_encoded_result`.
- `GroupKeyRefUnsafe` stores a raw pointer plus begin/end offsets into `group_key_buffer` and implements `Hash`, `PartialEq`, and `Eq` by dereferencing those ranges.

## Control Flow

Construction builds group-by RPN expressions and creates `AggregationExecutor::new`, which parses aggregate function descriptors and then calls `prepare_entities`. `prepare_entities` appends group-by result field types after aggregate result columns in the output schema.

On each input batch, `AggregationExecutor` calls `process_batch_input`. The slow hash implementation first decodes all source columns needed by the group-by expressions, then evaluates group-by RPN expressions into `group_by_results_unsafe` with erased lifetimes. For each logical row, it appends sort-key encoded group-by values to `group_key_buffer`. Byte-typed group-by expressions are stored twice: sort-key form for grouping and original datum form for later output. Scalar expression encodings are cached in `cached_encoded_result` so constants do not re-encode for every row.

After encoding a candidate key, the executor builds a `GroupKeyRefUnsafe` over the sort-key slice and probes `groups`. A vacant entry gets the next group index and creates one aggregate state per aggregate function. An occupied entry truncates the newly appended duplicate key material and offsets, then reuses the existing group index. The selected state offset is recorded per logical row. Finally, `HashAggregationHelper::update_each_row_states_by_offset` evaluates aggregate argument expressions and updates the correct group state for each row.

The executor only emits after the source is drained. `iterate_available_groups` asserts `src_is_drained.stop()`, takes the `groups` map, iterates group indices, pushes aggregate results through the shared iteratee, and reconstructs group-by output columns from `group_key_buffer` and `group_key_offsets`. Because hash map iteration order is unspecified, output group order is intentionally unstable.

## State and Persistence Behavior

All state is in-memory and per executor instance. There is no durable persistence. `states` persists aggregate states across input batches until final output. `group_key_buffer` and `group_key_offsets` retain the canonical encoded key material for unique groups; duplicate row keys are rolled back immediately. `group_by_results_unsafe` contains batch-local expression outputs and is explicitly cleared after updating states. `cached_encoded_result` persists encoded scalar group-by values for the lifetime of the executor.

The unsafe key references require `group_key_buffer` to remain allocated and not move. The file boxes the `Vec<u8>` so the `Vec` object address is stable for `NonNull<Vec<u8>>`, while the vector's internal allocation may grow; `GroupKeyRefUnsafe` dereferences the current `Vec` and indexes by offsets, so it does not store raw element pointers.

## Dependencies and Integration Points

This executor integrates with `crate::interface::BatchExecutor`, the shared `util::aggr_executor::AggregationExecutor`, `tidb_query_aggr` aggregate function state/update traits, `tidb_query_expr` RPN expression evaluation, and `LazyBatchColumnVec` storage from `tidb_query_datatype`. It relies on `collections::HashMap` for grouping, `AllAggrDefinitionParser` for aggregate metadata, and `HashAggregationHelper` for row-to-state updates. Runtime drain, paging, warnings, stats, scanned ranges, and storage stats are handled by the shared aggregation wrapper and source executor.

## Risks and Edge Cases

- The file-level FIXME is a real correctness risk: serialized group keys may not be semantically correct for all SQL equality/collation cases.
- Unsafe lifetime erasure and raw pointer key wrappers demand strict ownership discipline. Any future mutation that invalidates offsets or moves the boxed `Vec` object would be dangerous.
- Hash output order is nondeterministic, so consumers and tests must not depend on order unless sorted externally.
- The executor withholds all results until source drain; memory grows with number of groups and stored key bytes. Paging can force a `PagingDrain` once group count reaches the configured threshold, but partial result readiness remains `false` in this implementation.
- `check_supported` asserts non-empty group-by; this executor is not the no-group aggregate path.

## Test Signals

The integration test builds grouped aggregation over mixed `Real`, `Bytes`, nullable values, constants, arithmetic expressions, and UTF-8 collation. It verifies empty batches before drain, final group count, output schema cardinality, aggregate results, original byte group-by output, scalar group-by values, and order-independent validation by sorting returned groups. Shared aggregation paging tests in `util/aggr_executor.rs` also exercise slow hash behavior with paging sizes.
