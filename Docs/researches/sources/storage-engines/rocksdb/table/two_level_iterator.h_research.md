# sources/storage-engines/rocksdb/table/two_level_iterator.h

Purpose: declares the two-level iterator abstraction used for partitioned table/index traversal. A first-level iterator points at block handles, and the returned iterator exposes a single ordered stream from the corresponding second-level iterators.

Important APIs/types: `TwoLevelIteratorState` is the extension point with virtual `NewSecondaryIterator(const BlockHandle&)`. `NewTwoLevelIterator(TwoLevelIteratorState*, InternalIteratorBase<IndexValue>*)` constructs the flattening iterator and transfers ownership of both the state and first-level iterator to the implementation.

Control flow and integration: callers provide an index iterator whose values contain `IndexValue::handle`. On demand, the implementation asks the state object for a secondary iterator over the pointed-to block. This header intentionally keeps block loading policy out of the iterator interface.

State and persistence behavior: the header declares no durable state. Its ownership contract is important: first-level and secondary iterators are expected not to be arena allocated.

Dependencies: includes RocksDB env/iterator APIs and `table/iterator_wrapper.h`; forward declares `ReadOptions` and `InternalKeyComparator`.

Risks and test signals: any implementer of `TwoLevelIteratorState` must return heap-owned `InternalIteratorBase<IndexValue>` instances or null on failure. Tests should verify ownership, null secondary behavior, partition transitions, and ordering equivalence with a flat iterator.
