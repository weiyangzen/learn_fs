# sources/storage-engines/tikv/components/tidb_query_executors/src/partition_top_n_executor.rs

## Purpose

`partition_top_n_executor.rs` implements `BatchPartitionTopNExecutor`, a vectorized TiKV coprocessor executor for `TOP N ... PARTITION BY ...` and for partitioned `LIMIT` without order keys. It sits between a child `BatchExecutor` and the runner, keeps a bounded `TopNHeap` per currently observed partition, and emits rows when a partition boundary is seen or the child drains. The code assumes input is sorted by the partition expressions for early per-partition flushing; if input is not ordered, the executor remains safe for the two-stage TopN plan but treats non-contiguous equal keys as separate local partitions.

## Important APIs, Types, and Functions

- `BatchPartitionTopNExecutor<Src>` stores the child executor, evaluation context, partition/order RPN expressions, return field types, ordering flags, heap state, and the last partition key.
- `new(config, src, partition_exprs_def, order_exprs_def, order_is_desc, n)` builds RPN expressions with `RpnExpressionBuilder::build_from_expr_tree`, derives expression return field types from the child schema, creates the heap, and initializes evaluation context and partition comparison metadata.
- `new_for_test` and `new_for_test_with_config` mirror construction for test-built RPN expressions and support explicit paging configuration.
- `check_partition_equal_or_update(current)` compares the incoming partition key with `last_partition_key` using `HeapItemUnsafe` comparison logic. On inequality it stores the new key and returns false.
- `handle_next_batch()` reads one child batch, decodes columns required by order and partition expressions, evaluates expressions with `eval_exprs_decoded_no_lifetime`, wraps source batch data in `Arc<HeapItemSourceData>`, pushes order rows into `TopNHeap`, and flushes heap contents on partition changes or final drain.
- `next_batch(scan_rows)` implements the `BatchExecutor` contract. It short-circuits `n == 0`, optionally bypasses the optimization when `2 * n > paging_size`, converts flushed columns into logical rows `0..rows_len`, and returns evaluation warnings or errors.
- The `BatchExecutor` delegation methods forward schema, intermediate output, stats, storage stats, scanned range, and cacheability to the child.

The executor uses `HeapItemUnsafe` and `TopNHeap` from `crate::util::top_n_heap`. `HeapItemUnsafe` stores non-owning pointers to expression evaluation buffers, field type arrays, order flags, and source batch data. The executor marks itself `Send` with an explicit unsafe impl because these pointers remain internal and are not intentionally shared across threads.

## Control Flow

Construction is descriptor driven: the DAG runner extracts `partition_by` and `order_by` expressions from `Limit` or `TopN` descriptors and calls `BatchPartitionTopNExecutor::new`. During each `next_batch` call, the executor fetches up to `BATCH_MAX_SIZE` rows from its child, installs the child warnings into its `EvalContext`, and reads the child drain status. Empty child logical rows are skipped except that a final drain still flushes pending heap contents.

For non-empty batches, the executor first ensures all order and partition referenced columns are decoded. It pins the batch data in an `Arc`, evaluates order expressions into `eval_columns_buffer_unsafe`, records the offset, then evaluates partition expressions into the same buffer and records a second offset. For every logical row, it creates a partition-key `HeapItemUnsafe`; if it differs from `last_partition_key`, all rows currently retained in the heap are appended to the output columns and the heap is reset to capacity `n`. It then creates an order-key `HeapItemUnsafe` for the same row and inserts it into the heap. If the child reports a stop drain, the remaining heap rows are appended as the final partition.

The output `LazyBatchColumnVec` built by `TopNHeap::take_all_append_to` is already materialized as result columns, so `next_batch` resets output logical rows to a dense range. Errors from expression evaluation or heap comparison are returned through `BatchExecuteResult.is_drained = Err(...)` with warnings taken from the context and no data.

## State and Persistence Behavior

All state is volatile and per executor instance. Persistent state is not written. Important mutable state includes:

- `heap`: retained best rows for the current partition only.
- `last_partition_key`: current partition identity, represented as a reusable heap item.
- `eval_columns_buffer_unsafe`: an append-only buffer of expression results referenced by unsafe heap items. Its lifetime is tied to the executor and source batch `Arc`s.
- `context.warnings`: accumulated expression warnings; consumed with `take_warnings` after each public batch.

The executor relies on child executors for scanned range and storage statistics. It does not maintain its own range cursor. The paging guard is notable state behavior: when `paging_size` exists and `n * 2 > paging_size`, the executor bypasses local partition TopN and simply returns child batches. This avoids worst-case output growth above a page target but means the optimization can be disabled by request configuration.

## Dependencies and Integration Points

This file integrates with:

- `crate::interface::{BatchExecutor, BatchExecuteResult, BatchExecIsDrain, ExecuteStats}` for the vectorized executor contract.
- `tidb_query_expr::{RpnExpression, RpnExpressionBuilder, RpnStackNode}` for descriptor parsing and vector expression evaluation.
- `tidb_query_datatype::codec::batch::LazyBatchColumnVec` and `data_type::BATCH_MAX_SIZE` for columnar batch data.
- `crate::util::{ensure_columns_decoded, eval_exprs_decoded_no_lifetime, top_n_heap::*}` for decoded expression input and heap ordering.
- `runner.rs`, where partitioned `Limit` and partitioned `TopN` descriptors are mapped to this executor.

The executor preserves the child schema because partition TopN filters/reorders rows but does not add or remove result columns. Intermediate result APIs are delegated so it can be composed above index lookup or other executors that expose intermediate outputs.

## Risks and Edge Cases

- The unsafe pointer design is the primary risk. `eval_columns_buffer_unsafe` and `HeapItemUnsafe` must not be moved, cleared, or exposed in a way that invalidates internal pointers while heap items remain. The `Send` impl relies on this invariant.
- Partition correctness depends on input partition ordering for single-stage semantics. The file comment and test show unordered keys are treated as separate partitions; correctness is expected only after the plan's second-stage TopN.
- Memory can exceed the caller's requested page size in boundary cases. The code documents a worst case of `2*n - 1` output rows and uses a bypass guard when `2*n > paging_size`.
- `last_partition_key` compares via heap item equality with dummy `partition_is_desc` flags. This reuses sort-key comparison machinery and is marked for future refactoring.
- Expression errors clear the output for the batch and surface as executor drain errors. Partial rows before an error are not emitted.
- Empty order expression lists are supported and behave as first `n` rows per partition according to heap behavior; tests cover partitioned limit without order keys.

## Test Signals

The module has extensive unit tests using `MockExecutor`. Covered signals include `n == 0`, constant partitions, multiple and null partition keys, partition expressions, descending and ascending order, unordered partition keys, integrated byte and timestamp-like data, paging size interactions, no-partition behavior copied from TopN tests, unsigned integer ordering, collation-sensitive bytes ordering, and pass-through behavior when paging limits make local TopN unsafe. These tests also exercise empty child batches and multi-call draining behavior.
