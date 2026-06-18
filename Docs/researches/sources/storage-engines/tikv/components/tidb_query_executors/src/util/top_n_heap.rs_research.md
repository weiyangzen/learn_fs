# sources/storage-engines/tikv/components/tidb_query_executors/src/util/top_n_heap.rs

## Purpose

`util/top_n_heap.rs` implements the heap data structure used by TopN-like executors. It keeps the best N rows according to pre-evaluated order expressions and materializes retained rows back into a `LazyBatchColumnVec`.

## Important APIs, Types, and Functions

- `TopNHeap` stores `n` and a `BinaryHeap<HeapItemUnsafe>`.
- `TopNHeap::new` caps initial heap capacity at `min(n, 1024)` to avoid large allocation spikes.
- `add_row` validates a row's comparability, pushes while under capacity, and otherwise replaces the current greatest row if the new row sorts smaller.
- `take_all_append_to` drains the heap, obtains sorted items with `into_sorted_vec`, creates/appends result columns, preserves extra common handle keys, and copies raw or decoded values from source rows.
- `take_all` materializes into a new empty column vector.
- `HeapItemSourceData` pins a source batch's physical columns and logical rows.
- `HeapItemUnsafe` holds non-null pointers to order flags, order field types, and evaluation results, plus an `Arc` to source data and a logical row index.
- `HeapItemUnsafe::cmp_sort_key` compares order expression scalar refs by field type and desc flags.

## Control Flow

TopN executors create a `HeapItemUnsafe` for each logical row after order expressions have been evaluated into an executor-owned buffer. `add_row` maintains a max heap where the worst retained row is at the top. If the heap is not full, the row is pushed after self-comparison validates collator/order expression data. If full, the row is compared with the current greatest row and replaces it only when it should rank earlier.

On output, `take_all_append_to` drains the heap and iterates sorted items. It initializes result columns from the first source batch's column shape when needed, handles extra common handle keys, and then copies each retained row's values column by column. Raw columns push raw datum slices; decoded columns borrow typed values and clone owned values into destination vectors. Column lengths are asserted at the end.

## State and Persistence Behavior

State is in-memory and emptied by `take_all`/`take_all_append_to`. Heap items keep source batches alive through `Arc<HeapItemSourceData>`, while unsafe pointers assume the parent executor's order metadata and evaluation buffer remain alive and unmoved. No durable persistence exists.

## Dependencies and Integration Points

The module depends on `BinaryHeap`, `Arc`, `NonNull`, `LazyBatchColumnVec`, `LazyBatchColumn`, vector datatypes, `RpnStackNode`, `FieldType`, and TiKV logging. It is consumed by `BatchTopNExecutor` and any future TopN-like batch executor.

## Risks and Edge Cases

- `HeapItemUnsafe::Ord` unwraps comparison results and can panic if data was not validated. `add_row` self-compares before insertion to reduce this risk.
- Unsafe non-null pointers rely on parent executor field lifetimes and drop order.
- `take_all_append_to` has a TODO for schema equality; it currently asserts only column count.
- Missing extra common handle keys log an error and push an empty key, which avoids panic but may degrade correctness for consumers needing handle keys.
- Cloning decoded values is marked as potentially unnecessary and may be a performance cost.
- `add_row` assumes `self.heap.peek_mut().unwrap()` when full; if `n == 0`, callers should avoid adding rows. `BatchTopNExecutor` handles `n == 0` before processing.

## Test Signals

There are no direct tests in this file. It is exercised by `top_n_executor.rs` tests that validate ordering, nulls, collations, unsigned integer comparison, extra common handle key propagation, and heap output materialization.
