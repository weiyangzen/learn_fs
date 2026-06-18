# sources/storage-engines/tikv/components/tidb_query_executors/src/limit_executor.rs

## Purpose
`limit_executor.rs` implements `BatchLimitExecutor`, a parent executor that wraps another `BatchExecutor` and truncates the number of logical rows returned. It supports ordinary SQL `LIMIT` behavior and a rank-limit mode that returns all rows tied with the Nth row according to one or more truncate-key expressions. The rank-limit mode is used for top-N/rank-style semantics where peers with equal ordering keys must not be split.

## Important APIs, Types, and Functions
- `BatchLimitExecutor<Src>`: generic wrapper over a source executor. It stores the child, remaining row budget, whether the child is a scan executor, evaluation context, truncate-key expressions, truncate-key field types, previous/current key buffers, and debug-only execution flags.
- `new(src, limit, is_src_scan_executor)`: constructs a normal limit with no truncate-key expressions and default eval config.
- `new_rank_limit` and `new_rank_limit_impl`: construct rank-limit mode from TiDB `Expr` definitions or already-built `RpnExpression`s.
- `new_rank_limit_for_test` and `into_child`: test helpers.
- `record_truncate_key_values`: decodes/evaluates truncate-key expressions for a selected logical row and records owned previous key values.
- `cmp_row_truncate_key_with_prev`: compares current evaluated truncate keys against the previous boundary key using field-type sort semantics.
- `find_different_truncate_key_row`: evaluates truncate keys for a whole batch and binary-searches the first row whose keys differ from the recorded boundary.
- `BatchExecutor` implementation: delegates schema/intermediate/stats/storage/range/cache methods and implements the limiting logic in `next_batch`.

## Control Flow
For normal limit mode, `next_batch` optionally reduces `scan_rows` to `min(scan_rows, remaining_rows)` when the child is a scan executor. It then pulls one child batch, records a batch-limit work metric using child logical row count, subtracts returned rows from `remaining_rows`, truncates `logical_rows` when the row budget is reached, marks the result as `Drain`, and returns the batch without changing physical columns.

Rank-limit mode starts similarly but has additional peer-group handling. If the configured limit is zero and no boundary key has been recorded, it returns an empty drained result immediately. If `real_scan_rows` becomes zero, it uses `runner::BATCH_MAX_SIZE` so it can still fetch rows to determine peer groups. After pulling a child batch, it records work metrics and exits early for empty batches. If the whole batch fits in the remaining budget, it emits it and, when the budget reaches zero, records truncate keys from the last emitted row. If the batch exceeds the remaining budget, it records the Nth row's truncate keys if needed, evaluates truncate keys for the batch, binary-searches for the first row with a different key, emits rows through that peer group, sets remaining rows to zero, and marks drain when output is shorter than the child batch.

The executor never compacts physical columns. It only truncates `logical_rows`, preserving physical storage and extra common handle keys from the source. Errors from decode/evaluation are returned in `is_drained: Err(err)` with the current physical/logical data attached.

## State and Persistence Behavior
`remaining_rows` is the central mutable state and persists across `next_batch` calls. In rank-limit mode, `prev_truncate_keys` stores owned scalar values for the boundary row after the nominal limit is reached; subsequent batches compare against that boundary to include all tied peers. `current_truncate_keys_unsafe` is a reusable expression-result buffer whose contents are only valid for the current batch despite its `'static` type parameter; the code confines its use to the active batch. `EvalContext` stores evaluation behavior and warnings. There is no durable persistence.

## Dependencies and Integration Points
- Implements the `BatchExecutor` trait from `interface.rs` and delegates most behavior to the source executor.
- Uses `LazyBatchColumnVec`, `ScalarValue`, `ScalarValueRef`, and `EvalWarnings` from `tidb_query_datatype`.
- Uses `tidb_query_expr::{RpnExpression, RpnExpressionBuilder, RpnStackNode}` for rank-limit truncate-key evaluation.
- Uses utility functions `ensure_columns_decoded` and `eval_exprs_decoded_no_lifetime` to decode/evaluate child columns.
- Uses `tipb::Expr` and `FieldType` as pushed-down expression/schema inputs.
- Records executor work metrics under `ExecutorName::batch_limit`.
- Refers to `crate::runner::BATCH_MAX_SIZE` when rank-limit needs to fetch after the ordinary scan row count reaches zero.

## Risks and Edge Cases
- Rank-limit correctness relies on input rows being sorted by truncate keys. The binary search assumes equal-to-boundary rows form a prefix of the remaining batch.
- The unsafe expression-result buffer is lifetime-sensitive. It is safe only because values are consumed within the same batch and owned copies are stored in `prev_truncate_keys`.
- Normal limit mode marks the result drained once it has emitted the limit, even if the child batch carried an error. Existing tests indicate the limit boundary suppresses a later child error in that batch.
- Empty batches with `Remain` must pass through so callers can continue pulling.
- `is_src_scan_executor` changes scan volume by reducing requested rows. Incorrectly setting it can affect how much work the child scan performs and how scanned ranges/paging behave.
- Physical columns are not truncated, so downstream consumers must use `logical_rows` and must preserve associated extra common handle key semantics.
- Rank-limit with `limit == 0` returns immediately only before any boundary key is recorded; after a boundary is known, it still needs to consume peer rows until keys differ.

## Test Signals
The test module covers normal limit zero, child errors before the limit, child drain before the limit, errors at the limit boundary, drain after the limit across empty batches, scan-source row-count reduction, and preservation of `extra_common_handle_keys`. Rank-limit tests cover zero limit, one-batch peer inclusion for several limits, full-batch decode when the same batch is reused for comparison, multi-batch peer groups crossing batch boundaries, and case-insensitive collation comparison. Debug-only flags verify whether normal or rank-limit paths executed.
