# sources/storage-engines/tikv/components/tidb_query_executors/src/stream_aggr_executor.rs

## Purpose

`stream_aggr_executor.rs` implements `BatchStreamAggregationExecutor`, the batch executor for stream aggregation. It assumes rows are already ordered by the GROUP BY keys, so it can aggregate consecutive equal keys and release complete groups before the entire source is drained. This makes it lower-memory than hash aggregation for sorted streams.

## Important APIs, Types, and Functions

- `BatchStreamAggregationExecutor<Src>` wraps `AggregationExecutor<Src, BatchStreamAggregationImpl>` and forwards the `BatchExecutor` interface.
- `check_supported` requires non-empty group-by expressions, validates group-by RPN support, and validates aggregate functions through `AllAggrDefinitionParser`.
- `new` builds RPN group-by expressions from protobuf descriptors and delegates to `new_impl`.
- `BatchStreamAggregationImpl` stores `group_by_exps`, `group_by_exps_types`, `group_by_field_type`, the current buffered group `keys`, aggregate `states`, and unsafe expression result buffers for group-by and aggregate arguments.
- `update_current_states` updates the most recent group's aggregate states for a logical row range, with scalar inputs handled via `update_repeat!` and vector inputs via `update_vector!`.

## Control Flow

Construction records group-by field types and eval types, creates the concrete implementation, and passes it to the shared aggregation wrapper. `prepare_entities` appends group-by fields after aggregate result columns.

For each source batch, `process_batch_input` decodes all columns used by both group-by expressions and aggregate argument expressions, evaluates both sets into batch-local unsafe buffers, then scans logical rows in order. For each row it forms scalar references for the group key and compares them with the last buffered key via `ScalarValueRef::cmp_sort_key` and the group-by field type. If the key matches the last group, it continues accumulating. If the key changes, it updates the previous current group over the row range `[group_start_logical_row, logical_row_idx)`, stores the new key as owned `ScalarValue`s, creates one state per aggregate function, and starts a new group. After the loop, it updates the current group over the remaining range.

`iterate_available_groups` is where stream aggregation differs from hash aggregation. If the source is drained, all buffered groups are complete. If the source remains, the trailing group might continue in a future batch, so it emits only `groups_len - 1` groups. It drains the emitted states and keys from the front of the vectors, pushes aggregate result columns through the shared iteratee, and materializes group-by columns as decoded columns. `is_partial_results_ready` returns true once at least two groups are buffered, because that means at least one complete group is available.

## State and Persistence Behavior

The executor keeps only the not-yet-emitted group keys and aggregate states in memory. Complete groups are drained from `keys` and `states` whenever partial results are emitted. The last group is retained across batch boundaries until a different key arrives or the source drains. Unsafe expression result buffers are batch-local allocation reuse buffers and are cleared after processing each batch. There is no durable persistence.

## Dependencies and Integration Points

The file integrates with `AggregationExecutor`, `BatchExecutor`, `tidb_query_aggr` state/update macros, `tidb_query_expr` RPN evaluation, and `tidb_query_datatype` scalar comparison/collation behavior. It delegates warning/drain/result wrapping and paging to the shared aggregation executor. Its correctness depends on an upstream planner or executor preserving GROUP BY sort order.

## Risks and Edge Cases

- The executor assumes sorted input. If upstream ordering is wrong, equal groups separated by another group will be emitted as separate groups.
- Partial emission excludes the trailing group; arithmetic around `groups_len - 1` is guarded by `is_partial_results_ready`, but future changes must preserve that invariant.
- Unsafe lifetime erasure is used for expression result buffers. Results must not outlive the current batch.
- Group comparison uses sort-key semantics and field types, making collation correctness dependent on datatype comparison implementation.
- The no-aggregate-function case is supported: groups can be emitted with only GROUP BY columns.

## Test Signals

Tests cover normal stream aggregation with `COUNT` and `AVG`, nulls, arithmetic expressions, UTF-8 general collation, partial output before drain, empty intermediate batches, final drain output, and a query shape with GROUP BY columns but no aggregate functions. Shared paging tests compare stream aggregation with hash variants and verify partial output row counts under paging sizes.
