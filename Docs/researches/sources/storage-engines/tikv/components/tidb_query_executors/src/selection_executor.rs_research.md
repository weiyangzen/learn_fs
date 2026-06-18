# sources/storage-engines/tikv/components/tidb_query_executors/src/selection_executor.rs

## Purpose

`selection_executor.rs` implements vectorized filtering for TiKV batch DAG execution. It evaluates one or more boolean-like RPN predicates over a child batch and mutates the batch logical row list so only rows satisfying every predicate remain. Physical columns are reused; selection does not materialize new result columns.

## Important APIs, Types, and Functions

- `BatchSelectionExecutor<Src>` stores an `EvalContext`, child executor, predicate RPN expressions, and a precomputed column-reference count per predicate.
- `check_supported(descriptor: &Selection)` validates that every selection condition can be converted to supported RPN evaluation.
- `new(config, src, conditions_def)` parses tipb `Expr` predicate trees into `RpnExpression`s and records `count_column_refs` for work metrics.
- `new_for_test` and `into_child` support unit tests.
- `handle_src_result(src_result)` mutates `src_result.logical_rows` by evaluating predicates in order, short-circuiting once no rows remain.
- `count_column_refs(expr)` counts `RpnExpressionNode::ColumnRef` nodes with saturating conversion to `u32`.
- `update_logical_rows_by_scalar_value(...)` applies scalar predicate truthiness to all rows.
- `update_logical_rows_by_vector_value(...)` applies vector predicate truthiness row by row using `retain`.
- `next_batch(scan_rows)` delegates to the child, runs filtering, merges warnings on success, or clears all rows and attaches an error on predicate failure.

## Control Flow

Each public batch starts by fetching one child `BatchExecuteResult`. `handle_src_result` ignores any child drain error comment-wise, but predicate evaluation can still be skipped naturally if logical rows are empty. For each predicate, it clones the current logical row list into a scratch vector because expression evaluation needs the pre-filter row mapping while the original row list will be retained in place.

Before evaluating a predicate, the executor records approximate work as:

`rows * (rpn_node_count + column_ref_count)`

using `tidb_query_common::metrics::record_executor_work` with executor name `batch_selection`. It then evaluates the predicate. Scalar results are converted to MySQL boolean once; false clears all logical rows and true preserves all. Vector results are interpreted through the value's logical row mapping and MySQL truthiness, retaining only rows whose predicate value is true. Nulls convert through `AsMySqlBool` semantics, so they filter out as false. The loop stops when either all predicates have run or no logical rows remain.

If predicate evaluation or boolean conversion returns an error, `next_batch` combines that error into `is_drained`, clears all rows, and does not merge accumulated warnings. On success it merges evaluation warnings into the child warnings and returns the same physical columns with the reduced logical row list.

## State and Persistence Behavior

Selection maintains no durable state. It mutates only per-batch logical row vectors and its `EvalContext` warnings. Physical column storage, extra common handle keys, scan stats, storage stats, and range state remain owned by the child. Because the executor preserves the child physical columns, extra common handle keys remain unfiltered at the column-vector level and consumers must continue to respect logical rows.

## Dependencies and Integration Points

This file integrates with:

- `crate::interface` for `BatchExecutor` and batch result structures.
- `tidb_query_expr::{RpnExpression, RpnExpressionBuilder, RpnStackNode}` for predicate evaluation.
- `tidb_query_datatype::{match_template_evaltype, AsMySqlBool, ChunkRef, EvaluableRef, LogicalRows}` for typed vector truth conversion.
- Metrics via `tidb_query_common::metrics::record_executor_work`.
- `runner.rs`, which creates this executor for `ExecType::TypeSelection` and validates descriptors through `check_supported`.

Selection preserves the child schema and delegates intermediate result behavior, so it can be placed above scans, index lookup, or other operators without changing output column layout.

## Risks and Edge Cases

- On the first predicate error, the whole batch is dropped. A test notes a more precise future behavior could return innocent rows before the failing row.
- `src_logical_rows_copy` allocates per batch and is reused per predicate; the TODO calls out avoiding this allocation.
- Work metrics are approximate and deliberately weight column references in addition to RPN nodes.
- Since physical columns are not compacted, metadata and consumers must honor logical rows. Extra common handle keys are preserved unfiltered.
- Empty logical rows must not call predicate functions; tests enforce this with unreachable functions.
- Multiple predicates short-circuit only after each predicate; there is no row-level short-circuit across predicates inside a single expression.

## Test Signals

Tests cover empty batches, no predicate, always-true and always-false predicates, single and multiple predicates in different orders, predicate errors, and preservation of extra common handle keys with filtered logical rows. They assert logical row indexes and drain/error behavior across multiple child batches.
