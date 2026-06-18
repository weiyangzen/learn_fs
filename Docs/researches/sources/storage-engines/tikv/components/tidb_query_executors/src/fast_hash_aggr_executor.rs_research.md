# sources/storage-engines/tikv/components/tidb_query_executors/src/fast_hash_aggr_executor.rs

## Purpose
This file implements `BatchFastHashAggregationExecutor`, a vectorized hash aggregation executor optimized for exactly one group-by expression. It hashes typed group keys directly instead of using the slower general multi-key aggregation path.

## Important APIs, types, and functions
`BatchFastHashAggregationExecutor<Src>` wraps generic `AggregationExecutor<Src, FastHashAggregationImpl>` and delegates the `BatchExecutor` API. `check_supported` rejects multi-column group-by, unsupported group-by eval types, unsupported RPN expressions, and unsupported aggregate definitions.

`new` builds a single RPN group-by expression from tipb expressions and delegates to `new_impl`. `new_impl` derives the group-by field type and eval type, then creates a typed `Groups` hash map. `Groups` stores `HashMap<Option<T>, usize>` variants for int, real, bytes, duration, decimal, datetime, enum, and vector float32 keys, where the value is an offset into the aggregate state vector.

`FastHashAggregationImpl` owns aggregate states, typed groups, the group-by expression, output group-by field type, and per-input-row state offsets. It implements `AggregationExecutorImpl`.

## Control flow
For each input batch, `process_batch_input` evaluates the group-by expression over source columns. Scalar group results route through `handle_scalar_group_each_row`, creating one state group and assigning every logical row to offset 0. Vector results route through `calc_groups_each_row`, which maps each logical row value into a hash key, reuses existing state offsets, or appends new aggregate states for new groups. Bytes grouping is collation-aware: it transmutes the group map to use `SortKey<Bytes, Collator>` under the selected collation and stores sort keys as grouping identities.

After group offsets are computed, `HashAggregationHelper::update_each_row_states_by_offset` evaluates aggregate arguments and updates states. Results are only emitted after the source is drained. `iterate_available_groups` takes the group map, calls the result iteratee over each group's state slice, and builds a decoded group-by output column.

## State and persistence behavior
State is in-memory only. Aggregate states are append-only until final output; group maps point into the `states` vector. `states_offset_each_logical_row` is cleared and reused each batch. `iterate_available_groups` consumes groups with `mem::take`, so output is a terminal phase for this implementation.

## Dependencies and integration points
The executor depends on `tidb_query_aggr` for aggregate function definitions/states, `tidb_query_expr` for RPN evaluation, datatype vector/field/collation APIs, `AggregationExecutor` shared machinery, and `HashAggregationHelper` for updating states. Metrics record work under `batch_fast_hash_aggr`.

## Risks and edge cases
The executor assumes exactly one group-by expression and no partial output before drain, so memory grows with group cardinality and aggregate state size. Bytes grouping uses unsafe transmute to reinterpret the hash map key type for collation sort keys; this depends on identical representation expectations and is a sensitive maintenance area. Scalar group handling panics if a supposedly constant expression produces a different value on later batches. Support checking excludes `EvalType::Enum`, but implementation and tests include enum grouping through direct test construction, so production support and internal capability differ.

## Test signals
Tests compare fast and slow hash aggregation on integration cases, constant group-by, collation grouping, no-row input, no aggregate functions, and enum column grouping. They validate output schemas, group counts, warning propagation through mock executors, and undefined row order handling by sorting before assertions.
