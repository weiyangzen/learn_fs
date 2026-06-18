# sources/storage-engines/tikv/components/tidb_query_executors/src/util/mod.rs

## Purpose

`util/mod.rs` declares shared executor utility modules and provides two common expression/column helpers used by aggregation and TopN executors.

## Important APIs, Types, and Functions

- Module exports: `aggr_executor`, `hash_aggr_helper`, test-only `mock_executor`, `scan_executor`, and `top_n_heap`.
- `ensure_columns_decoded` iterates over RPN expressions and asks each expression to decode any source columns it needs in the input `LazyBatchColumnVec`.
- `eval_exprs_decoded_no_lifetime` evaluates already-decoded expressions and appends `RpnStackNode` results into a caller-provided output vector after erasing lifetimes.

## Control Flow

Callers first use `ensure_columns_decoded` with an evaluation context, expression list, schema, mutable physical columns, and logical rows. Then, when they need to retain evaluated expression nodes in executor-owned buffers, they call the unsafe `eval_exprs_decoded_no_lifetime`. That function defines a local `erase_lifetime` helper, casts expression/schema/columns/logical-row references to a wider lifetime, evaluates each expression with `eval_decoded`, and pushes the result into the output vector.

## State and Persistence Behavior

The module has no own state. It mutates input columns by decoding lazy raw data and mutates the output vector by appending expression results. The lifetime-erased outputs are only valid as long as the referenced expressions, schemas, physical columns, and logical row slices stay alive according to the caller's safety contract.

## Dependencies and Integration Points

The helpers depend on `tidb_query_common::Result`, `LazyBatchColumnVec`, `EvalContext`, `tidb_query_expr::{RpnExpression, RpnStackNode}`, and `tipb::FieldType`. They are used by slow hash aggregation, stream aggregation, TopN, and likely other executor implementations needing batched expression evaluation.

## Risks and Edge Cases

- `eval_exprs_decoded_no_lifetime` is unsafe because it erases lifetimes. Callers must clear outputs before referenced batch data expires or pin referenced data for as long as outputs are used.
- `ensure_columns_decoded` may decode the same source column more than once across expressions unless lower layers deduplicate.
- The output vector is append-only; callers must account for existing offsets, as TopN does with `eval_offset`.

## Test Signals

There are no direct tests. The helpers are indirectly exercised by aggregation and TopN tests that evaluate group-by, aggregate, and order-by expressions over decoded columns.
