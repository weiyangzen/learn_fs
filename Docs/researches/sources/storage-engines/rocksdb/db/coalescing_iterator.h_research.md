# sources/storage-engines/rocksdb/db/coalescing_iterator.h

## Purpose
Declares `CoalescingIterator`, a RocksDB `Iterator` implementation that delegates multi-column-family positioning to `MultiCfIteratorImpl` and customizes value population by merging wide columns from all child iterators at the current logical key. It provides the ordinary `Iterator` surface while preserving coalesced wide-column results and a scalar default-column value.

## Important APIs, Types, And Members
The constructor accepts `ReadOptions`, a `Comparator`, and an rvalue vector of `(ColumnFamilyHandle*, unique_ptr<Iterator>)` pairs. These are forwarded into `MultiCfIteratorImpl<ResetFunc, PopulateFunc>` along with callbacks bound to the enclosing `CoalescingIterator`.

The public iterator API delegates almost entirely to `impl_`: `Valid`, `SeekToFirst`, `SeekToLast`, `Seek`, `SeekForPrev`, `Next`, `Prev`, `key`, `status`, and `PrepareValue`. `value()` returns `value_` and `columns()` returns `wide_columns_`, both requiring `Valid()`. `Reset()` clears `value_`, `wide_columns_`, and `owned_columns_`.

Private helper types are:

- `ResetFunc`: callback object that invokes `iter_->Reset()`.
- `PopulateFunc`: callback object that invokes `iter_->Coalesce(items)`.
- `WideColumnWithOrder`: heap item containing a `WideColumn` pointer and a child order.
- `WideColumnWithOrderComparator`: comparator that orders heap items by column name and then by order.
- `MinHeap`: `BinaryHeap<WideColumnWithOrder, WideColumnWithOrderComparator>`.

Private state consists of `impl_`, `value_`, `wide_columns_`, and `owned_columns_`. `owned_columns_` is a vector of copied `(name, value)` strings used to back the slices stored in `wide_columns_` and `value_`.

## Control Flow
All movement and seek operations are delegated to `MultiCfIteratorImpl`. When the delegated implementation needs to discard the current materialized value, it calls `ResetFunc`, clearing all coalesced result storage. When it needs to materialize the value/columns for the current key, it calls `PopulateFunc`, which passes the current matching `MultiCfIteratorInfo` set into `Coalesce`.

The `PrepareValue` override is also delegated to `impl_`, which means lazy value preparation, if any, is coordinated by the multi-CF implementation. Once prepared, callers retrieve the current coalesced key from `impl_.key()`, scalar value from `value_`, and wide-column set from `wide_columns_`.

## State And Persistence Behavior
`CoalescingIterator` has no persistent state; it is a transient read iterator. Its stateful behavior is about pointer validity and lifecycle. `value_` and `wide_columns_` expose slices, but the actual bytes are owned by `owned_columns_`, so values survive child iterator internal buffer reuse until the next reset. The class is non-copyable because it owns iterators and slice-backed result buffers.

`Reset` is the boundary between logical positions. It must run before new coalesced data is populated, otherwise stale slices could be exposed. The destructor is default-like and relies on member destructors for child iterator and buffer cleanup.

## Dependencies And Integration Points
The header depends on `db/multi_cf_iterator_impl.h` for movement, grouping, `MultiCfIteratorInfo`, `BinaryHeap`, and callback orchestration. It depends on RocksDB iterator abstractions (`Iterator`, `ReadOptions`, `Comparator`, `Slice`, `WideColumns`, `ColumnFamilyHandle`) and is implemented further in `coalescing_iterator.cc`.

This class is an adapter between the multi-CF iterator infrastructure and wide-column semantics. It lets higher-level code use a normal `Iterator` API over several column-family iterators while receiving a single coalesced wide-column view per key.

## Risks And Edge Cases
The class exposes `value()` and `columns()` only when valid, guarded by asserts. Callers in release builds still need to respect the `Iterator` contract. The callback objects store raw pointers to the parent iterator; this is safe only because they are embedded in `impl_` inside the parent and do not outlive it.

Tie-breaking for duplicate wide-column names is encoded in the heap comparator and implemented in `Coalesce`; mistakes there affect which column value wins. Because `value_` points into `owned_columns_` through `wide_columns_`, changing the storage container type or appending after taking slices would require careful lifetime review. The current `reserve(heap.size())` in the implementation is important to avoid vector reallocation invalidating stored string references while constructing `wide_columns_`.

## Test Signals
Header-level expectations are best validated through integration tests using real child iterators: movement delegates should keep key ordering stable across column families, `PrepareValue` should populate exactly once per logical position, `Reset` should clear stale values between keys, `columns()` should remain valid until movement, and `value()` should track the default wide column. Compile-time signal includes enforcing non-copyability and successful template instantiation with `MultiCfIteratorImpl<ResetFunc, PopulateFunc>`.
