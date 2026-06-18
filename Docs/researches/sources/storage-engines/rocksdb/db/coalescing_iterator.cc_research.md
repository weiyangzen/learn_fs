# sources/storage-engines/rocksdb/db/coalescing_iterator.cc

## Purpose
Implements `CoalescingIterator::Coalesce`, the value-population hook for an iterator that exposes a single logical key across multiple column-family iterators by coalescing their wide-column values. The implementation gathers wide columns from matching child iterators, chooses one value per column name according to the order supplied by `MultiCfIteratorImpl`, stores owned copies of the bytes, and exposes the default wide column as the iterator's scalar `value()` when present.

## Important APIs, Types, And Functions
The source includes `db/coalescing_iterator.h` and `db/wide/wide_columns_helper.h`. Its only function is:

- `void CoalescingIterator::Coalesce(const autovector<MultiCfIteratorInfo>& items)`: called by `MultiCfIteratorImpl` after it has found child iterator entries at the current coalesced key.

It uses the header-defined `MinHeap`, `WideColumnWithOrder`, and `WideColumnWithOrderComparator`. `MultiCfIteratorInfo` supplies an `iterator` pointer and an `order` field. The child `Iterator::columns()` API provides `WideColumn` entries, and `WideColumnsHelper::HasDefaultColumn`/`GetDefaultColumn` identify the conventional default column used to fill the scalar `value_` slice.

## Control Flow
`Coalesce` starts with assertions that `wide_columns_` and `owned_columns_` are empty. It creates a heap and pushes every wide column from every input child iterator, tagging each with the child order. If no columns exist, it returns and leaves the iterator's value/columns empty.

For non-empty input, it reserves storage sized to the heap, then defines `add_column`, which copies a wide column name and value into `owned_columns_` and appends a `WideColumn` pointing at those owned strings into `wide_columns_`. The heap is then popped in sorted order. When the next heap entry has a larger name than the current entry, the current column is emitted. When names compare equal, the current column is replaced by the later popped heap entry, so duplicates collapse to one emitted column. A comparison showing the current name greater than the heap top is treated as an impossible heap-order violation and asserted.

After the heap is drained, the last current column is emitted. If the final wide-column list contains a default column, `value_` is set to the default column's value slice.

## State And Persistence Behavior
This code has no disk persistence. Its important state is in-memory iterator result state:

- `owned_columns_` owns copied `std::string` name/value bytes.
- `wide_columns_` contains `WideColumn` objects whose slices point into `owned_columns_`.
- `value_` points to the default column value inside `wide_columns_` when present.

The explicit copies are a lifetime guard: coalesced results remain valid even if child iterators refresh or reuse internal buffers after the populate step. `Reset` in the header clears these containers before the next movement/repopulation cycle.

## Dependencies And Integration Points
`Coalesce` is integrated with `MultiCfIteratorImpl`, which handles movement and groups child iterators at a logical key before invoking the populate callback. It depends on each child iterator supporting the wide-column `columns()` API and on the ordering contract encoded by `MultiCfIteratorInfo::order`. It also depends on `BinaryHeap` semantics to provide ascending wide-column-name order through the custom comparator.

The scalar `Iterator::value()` compatibility path is integrated through `WideColumnsHelper`, so callers that only understand key/value entries still see the default wide column when coalesced data includes one.

## Risks And Edge Cases
Duplicate wide-column names are resolved by heap pop order and `item.order`; this makes the comparator's tie-break behavior critical. If the order semantics change in `MultiCfIteratorImpl`, coalescing precedence could silently change. The function asserts rather than reports an error for heap-order violations, so release builds may not catch impossible ordering issues explicitly.

The function assumes `Reset` was called before population, enforced by asserts. If future code calls `Coalesce` directly without clearing state, old columns could leak into the new logical result in non-assert builds. The empty-column case returns without setting `value_`, so callers rely on the reset path to avoid stale values.

## Test Signals
Useful tests should construct multiple child iterators that yield the same user key with disjoint and overlapping wide-column names, then verify sorted output column names, deterministic duplicate-name precedence, copied lifetime after child iterator movement, empty-column behavior, and scalar `value()` exposure when the default column is present. Integration tests should move forward and backward through a multi-CF coalescing iterator to confirm `Reset` and `PrepareValue` interactions.
