# sources/storage-engines/tikv/components/tidb_query_executors/src/top_n_executor.rs

## Purpose

`top_n_executor.rs` implements `BatchTopNExecutor`, a batch executor for ORDER BY ... LIMIT style top-N pushdown. It consumes its source to completion, evaluates order expressions, keeps only the best N rows in a heap, and emits sorted rows once the source is drained. It also has a paging shortcut where a TopN larger than the paging size is bypassed and source batches are returned directly.

## Important APIs, Types, and Functions

- `BatchTopNExecutor<Src>` implements `BatchExecutor` over any source executor.
- `check_supported` requires at least one order-by expression and validates each RPN expression tree.
- `new` converts protobuf order expressions into `RpnExpression`s and records return field types and descending flags.
- `handle_next_batch` pulls source batches at `BATCH_MAX_SIZE`, propagates warnings, processes rows into the heap, and returns heap output only when the source drains.
- `process_batch_input` records approximate comparison work metrics, decodes order-expression columns, pins source batch data in an `Arc<HeapItemSourceData>`, evaluates order expressions into `eval_columns_buffer_unsafe`, creates `HeapItemUnsafe` rows, and inserts them into `TopNHeap`.
- `next_batch` handles `n == 0`, paging bypass, error-to-empty-result behavior, remain-with-empty-output behavior, and final drain output.

## Control Flow

Construction stores the source, order expressions, order field types, order direction flags, evaluation context, heap, and reusable unsafe evaluation buffer. On each `next_batch`, `n == 0` immediately returns an empty drained result. If paging is configured and `n` exceeds paging size, the executor delegates directly to the source, effectively disabling TopN collection for that paging mode.

Otherwise, `handle_next_batch` reads the source using max batch size because TopN needs global ordering. For non-empty logical rows, `process_batch_input` ensures columns referenced by order expressions are decoded, evaluates order expressions, pins the full physical batch plus logical row mapping in an `Arc`, and adds each logical row to the heap. While the source remains, it returns empty remain results. On source drain, it calls `heap.take_all()` to materialize the retained rows in sorted order and returns a drained result.

Errors from the source or expression evaluation end the executor and produce empty columns with the error in `is_drained`, preserving warnings from the context.

## State and Persistence Behavior

State is in-memory. `TopNHeap` retains at most N `HeapItemUnsafe` records. Each heap item owns an `Arc` to the source batch data it references, so physical columns remain alive while any retained row points into them. `eval_columns_buffer_unsafe` accumulates evaluated order columns for processed batches and must outlive heap items; field order in the struct is deliberately arranged so heap drops before the data it points into. There is no durable persistence. After final output, the heap is drained.

## Dependencies and Integration Points

This executor integrates with `util::top_n_heap::{TopNHeap, HeapItemSourceData, HeapItemUnsafe}`, shared utility functions for decoding/evaluating RPN expressions, `tidb_query_expr`, `tidb_query_datatype` vector columns, `tidb_query_common::metrics::record_executor_work`, and `BatchExecutor` delegation for schema/intermediate results/stats/scanned ranges/cacheability.

## Risks and Edge Cases

- Unsafe pointers connect heap items to `order_is_desc`, order field types, and the evaluation buffer. The struct field order comments are part of the safety contract.
- TopN emits only after full drain unless paging bypass is active, so memory is bounded by N retained rows plus retained source batches for heap winners, but latency waits for the full source.
- When `n > paging_size`, the executor bypasses TopN and returns source order. That is an intentional paging behavior but surprising if callers expect global TopN in all modes.
- `eval_columns_buffer_unsafe` is not cleared after each batch because heap items may reference earlier evaluated columns. Long-running scans with many batches can retain expression result storage.
- Order comparison is non-stable for ties, matching test comments; callers must not require stable order among equal sort keys.
- Collation, unsigned integer ordering, null ordering, and expression errors depend on `ScalarValueRef::cmp_sort_key`.

## Test Signals

Tests cover `top 0`, empty logical batches, single and multi-column ordering, expression ordering, descending flags, null ordering, byte collations, unsigned integer ordering, paging bypass versus normal TopN, and propagation of extra common handle keys. The tests also confirm remain-empty outputs before source drain and final sorted outputs after drain.
