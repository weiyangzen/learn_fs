# Research: sources/storage-engines/rocksdb/table/iter_heap.h

- **Purpose:** Provides comparator functors for using `IteratorWrapper*` entries in `std::priority_queue` heaps for merging iterators.
- **Important APIs/types/functions:** `MaxIteratorComparator` and `MinIteratorComparator`, each constructed with an `InternalKeyComparator` and implementing `operator()(IteratorWrapper* a, IteratorWrapper* b)`.
- **Control flow:** The max comparator returns true when `a` is smaller than `b`, causing the largest key to be on top. The min comparator returns true when `a` is larger than `b`, causing the smallest key to be on top.
- **State and persistence behavior:** Each comparator stores only a raw pointer to the `InternalKeyComparator`; no persistent state or ownership is involved.
- **Dependencies:** Depends on internal key comparison from `db/dbformat.h` and cached iterator access through `IteratorWrapper`.
- **Integration points:** Used by `MergingIterator`-style code to select the next child iterator in forward or reverse order while merging multiple sorted sources.
- **Risks:** Assumes input wrappers are valid and positioned; `IteratorWrapper::key()` asserts validity. Comparator lifetime must outlive heaps using it. Tie behavior is delegated entirely to `InternalKeyComparator`.
- **Test signals:** `merger_test.cc` indirectly exercises min/max heap behavior through merged forward and reverse iteration equivalence against a single sorted vector iterator.
