# sources/storage-engines/tikv/components/tidb_query_executors/src/projection_executor.rs

## Purpose

`projection_executor.rs` implements the vectorized batch projection executor. It evaluates TiDB RPN expressions over a child batch and returns a new column set matching the projection expression list. It also contains a fast path for projections that are only non-duplicate column references, avoiding expression evaluation and unnecessary column copying.

## Important APIs, Types, and Functions

- `BatchProjectionExecutor<Src>` stores `EvalContext`, child executor, output schema, RPN expressions, and fast-path metadata.
- `check_supported(descriptor: &Projection)` validates every expression tree with `RpnExpressionBuilder::check_expr_tree_supported`.
- `get_schema_from_exprs(child_schema, exprs)` derives the projected schema from each expression return field type.
- `new(config, src, exprs_def)` parses tipb `Expr` descriptors into RPN expressions, detects the no-duplicate column-reference-only fast path, and builds the output schema.
- `new_for_test` performs the same setup for prebuilt test expressions.
- `check_column_ref(...)` recognizes a single-node `RpnExpressionNode::ColumnRef` and rejects duplicate offsets by tracking a `HashSet<usize>`.
- `next_batch(scan_rows)` pulls one child batch and either swaps out referenced columns directly or evaluates every expression into new `LazyBatchColumn`s.
- Standard `BatchExecutor` methods expose the projected schema and delegate intermediate results, stats, range, storage stats, and cacheability to the child.

## Control Flow

On construction, the executor walks projection expressions in order. While every expression is a single unique column reference, it records column offsets and keeps `no_dup_column_ref_only = true`. Any constant, function call, multi-node expression, or duplicate column reference disables the optimization.

At runtime `next_batch` gets one child `BatchExecuteResult`. It destructures drain status, logical rows, and warnings, but keeps mutable access to physical columns. If the child produced no logical rows or already carries a drain error, the executor skips evaluation and returns empty projected columns while preserving drain/error state.

For the fast path, the executor moves selected physical columns out of the child vector with a push-placeholder plus `swap_remove` trick. This avoids shifting all columns after each selected offset. Logical rows remain the child's original logical row indexes, and `extra_common_handle_keys` are preserved as-is because the physical row layout still corresponds to the child columns.

For the general path, it evaluates each RPN expression over the child's physical columns and current logical rows. Scalar results are expanded into a vector column with `VectorValue::from_scalar(..., logical_len)`, while vector results are taken directly. On the first expression error, the executor combines the error into `is_drained`, clears logical rows, and stops evaluating later expressions. If all expressions succeed, it compacts `extra_common_handle_keys` to match logical row order, resets logical rows to `0..logical_len`, and returns only projected columns.

At the end, child warnings and projection evaluation warnings are merged, and a `LazyBatchColumnVec::with_columns_and_extra_common_handle_keys` is returned.

## State and Persistence Behavior

The executor has no durable persistence. Runtime state is limited to the expression evaluation context and immutable construction metadata. `EvalContext` accumulates warnings across expression evaluations and is merged into child warnings before returning. Child storage/range state remains owned by the child.

The most important state distinction is physical/logical row indexing. The fast path preserves child logical rows and extra common handles. The general path creates freshly materialized projected columns and therefore normalizes logical rows to dense indexes, remapping common handle keys through the old logical rows.

## Dependencies and Integration Points

This file integrates with:

- `crate::interface` for the `BatchExecutor` trait and `BatchExecuteResult`.
- `tidb_query_expr::{RpnExpression, RpnExpressionBuilder, RpnExpressionNode}` for projection expression support.
- `tidb_query_datatype::codec::batch::{LazyBatchColumn, LazyBatchColumnVec}` and `VectorValue` for materialized batch columns.
- `runner.rs`, which constructs this executor for `ExecType::TypeProjection` and uses its schema for output-offset validation and encoding decisions.
- Index lookup/common handle support through `LazyBatchColumnVec` extra common handle key plumbing.

## Risks and Edge Cases

- The fast path uses `swap_remove` by original offsets. It is safe because it only enables when references are unique, but offset order and mutation need care. Future changes to allow duplicates must not use this path without preserving column semantics.
- General expression evaluation resets logical rows to dense indexes. Any metadata keyed by old physical rows must be explicitly remapped, as done for extra common handle keys.
- On expression error, all rows in the batch are dropped, even rows whose earlier expression results were valid.
- Empty projection expression lists produce no columns; only when `exprs` is non-empty and evaluation succeeds are logical rows normalized in the general branch.
- Warning merging must include both child and projection warnings; callers rely on warning counts in `runner.rs`.

## Test Signals

Tests cover empty child batches without invoking expression functions, constant projection, full column projection, simple expression projection, expression errors, and extra common handle propagation in both the fast and general paths. The tests assert logical rows, column counts, decoded values, drain states, and common handle key ordering.
