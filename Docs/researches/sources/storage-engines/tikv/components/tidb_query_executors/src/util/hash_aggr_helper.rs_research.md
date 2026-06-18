# sources/storage-engines/tikv/components/tidb_query_executors/src/util/hash_aggr_helper.rs

## Purpose

`util/hash_aggr_helper.rs` contains a shared helper for hash aggregation implementations. It updates aggregate function states when each logical input row may belong to a different group and the caller has already computed the state offset for every row.

## Important APIs, Types, and Functions

- `HashAggregationHelper` is a zero-sized namespace struct.
- `update_each_row_states_by_offset` accepts shared aggregation `Entities`, mutable input columns, logical rows, a flat slice of aggregate states, and `states_offset_each_logical_row`.
- It evaluates each aggregate argument expression once per aggregate function, then dispatches updates through `tidb_query_aggr::update!` for scalar and vector expression results.

## Control Flow

The helper loops over aggregate functions by index. For each function, it evaluates the corresponding aggregate argument RPN expression against the source schema, input physical columns, logical rows, and logical row count. If the expression result is scalar, the same scalar value is applied to every row's target state offset. If the result is vector, it zips each row's state offset with the expression result's logical row mapping and updates the state with the row-specific value. The `idx` is added to each row's group state offset to select the aggregate function state within that group.

## State and Persistence Behavior

The helper owns no persistent state. It mutates the caller-provided aggregate states and evaluation context. Any warnings or evaluation side effects accumulate in `entities.context`. Input columns may be used by expression evaluation and remain owned by the caller.

## Dependencies and Integration Points

This helper depends on `tidb_query_aggr::{AggrFunctionState, update}`, `RpnStackNode`, vector/scalar datatypes, and `Entities` from `aggr_executor`. It is used by hash aggregation executors after they map logical rows to group-state offsets.

## Risks and Edge Cases

- The `states_offset_each_logical_row` slice must align exactly with `input_logical_rows`; otherwise updates target wrong groups or panic on out-of-bounds state access.
- The flat state layout must be group-major with each group's aggregate states in aggregate definition order.
- Expression evaluation is repeated per aggregate function; shared common subexpressions are not cached here.
- Scalar aggregate arguments update every row with the same value, which is correct for constants but relies on expression evaluation's scalar/vector distinction.

## Test Signals

This file has no direct tests. It is exercised through slow and fast hash aggregation integration tests and shared aggregation paging tests, which validate grouped state updates for constants, vector expressions, nulls, and multi-batch input.
