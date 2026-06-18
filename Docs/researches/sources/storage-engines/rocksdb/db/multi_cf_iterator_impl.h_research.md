# sources/storage-engines/rocksdb/db/multi_cf_iterator_impl.h

## Purpose
`multi_cf_iterator_impl.h` implements the shared heap-based engine behind RocksDB iterators that merge multiple column-family iterators into one user-key stream. It supports both forward and reverse traversal, duplicate-key coalescing across column families, bounds inherited from child iterators, and deferred value materialization through `ReadOptions::allow_unprepared_value`.

## Important APIs, Types, And Functions
`MultiCfIteratorInfo` is the heap item: a column-family handle, a raw child `Iterator*`, and an `order` tie-breaker preserving the caller's column-family priority.

`MultiCfIteratorImpl<ResetFunc, PopulateFunc>` owns the child `(ColumnFamilyHandle*, unique_ptr<Iterator>)` pairs, the comparator, a status accumulator, and callback hooks. `reset_func_` is invoked before seeks/advances to clear higher-level coalesced state. `populate_func_` receives all heap entries for the current user key after values/columns have been prepared.

The public surface is iterator-like: `SeekToFirst`, `Seek`, `SeekToLast`, `SeekForPrev`, `Next`, `Prev`, `key`, `Valid`, `status`, and `PrepareValue`. Internally it uses a `std::variant` of `BinaryHeap` instances: `MultiCfMinHeap` for forward order and `MultiCfMaxHeap` for reverse order. `MultiCfHeapItemComparator` compares child iterator keys with the supplied RocksDB comparator and breaks equal-key ties by `order`.

## Control Flow
Seek operations switch to the correct heap direction through `GetHeap`, call `reset_func_`, clear the heap, seek every child iterator, and push valid children. If a child is invalid with a non-OK status, `considerStatus` records the first error and clears the heap so the composite iterator becomes invalid.

`Next` and `Prev` first ensure the heap direction matches the traversal. If switching direction, they rebuild the opposite heap around the current key via `Seek` or `SeekForPrev`. `AdvanceIterator` pops the top item, advances any other child iterators with the same key so duplicate keys appear only once, advances the original top iterator, and reinserts valid children. After a successful seek or advance, values are eagerly populated unless `allow_unprepared_value_` is enabled.

`PrepareValue` is meaningful only when unprepared values are allowed. It collects the current top entry and all same-key entries, calls each child iterator's `PrepareValue`, restores the heap, and calls `populate_func_` with the same-key group. A failed child preparation records the child status, clears the heap, and makes the multi-CF iterator invalid.

## State And Persistence Behavior
This header does not persist database state; it manages transient iterator state over child iterators created elsewhere. The important state is the active heap direction, current heap contents, accumulated `Status`, and any coalesced value/column state owned by the caller through `reset_func_` and `populate_func_`.

Duplicate-key elimination is stateful across advances. Child iterators that share the current user key are consumed together so a key is returned once even if several column families contain it. The `order` tie-breaker determines deterministic conflict resolution by controlling how same-key entries are ordered before population.

## Dependencies And Integration Points
The implementation depends on RocksDB `Iterator`, `ColumnFamilyHandle`, `Comparator`, `ReadOptions`, `Status`, `Slice`, `autovector`, and `util/heap.h`. It is designed to be embedded by higher-level coalescing and attribute-group iterators that define how same-key values or wide columns are combined.

Integration points include child iterator status semantics, child `PrepareValue`, comparator compatibility across column families, prefix-iteration behavior, and `ReadOptions::allow_unprepared_value`.

## Risks
All child iterators must use compatible comparators. A different comparator order can violate heap ordering, which is why callers/tests reject mixed comparator configurations.

The implementation assumes equal keys are grouped by comparator equality and that `order` is unique for same-key tie-breaking. If a child iterator becomes invalid because of manual prefix iteration, comments acknowledge the composite result is undefined. Direction switches rebuild heaps around copied current keys; any bug there can skip or repeat the current key.

Deferred value handling is error-sensitive. A child `PrepareValue` failure must invalidate the whole iterator so callers do not observe a key without a valid merged value.

## Test Signals
`multi_cf_iterator_test.cc` validates this engine indirectly through coalescing and attribute-group iterators: forward/reverse traversal, `Seek`/`SeekForPrev`, lower and upper bounds, empty column families, duplicate-key tie-breaking by column-family order, wide-column merging, same/different comparator handling, unprepared blob values, corruption propagation, snapshot auto-refresh, and blob-backed wide columns.
