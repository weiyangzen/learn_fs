# sources/storage-engines/rocksdb/table/compaction_merging_iterator.h

Purpose: declares the compaction-specific merging iterator factory and documents why compaction needs a specialized stream that includes range tombstone start keys.

Important APIs/types/functions: `NewCompactionMergingIterator` takes an internal key comparator, array of child `InternalIterator*`, child count, a vector of owned `TruncatedRangeDelIterator` pairs plus optional pointer backpatch slots, optional arena, and optional `InternalStats`.

Control flow: the factory returns an `InternalIterator` that merges point keys and synthetic range-deletion sentinel keys. The documentation explains that range tombstone starts are emitted as internal keys with `kTypeRangeDeletion` unless truncated at file boundaries.

State and persistence: no persistent state is declared. Ownership of range tombstone iterators is moved into the implementation. Child iterator ownership is transferred to the returned iterator.

Dependencies/integration: includes range deletion aggregation, merging iterator definitions, slices, types, and arena/stats forward declarations. It is used by compaction code rather than normal user iteration.

Risks and test signals: callers must use `IsDeleteRangeSentinelKey()` to distinguish range tombstone start keys from point entries, but the TODO notes that the same API is overloaded for file-boundary and range tombstone sentinels in different layers. Direct tests are absent here, so correctness depends on compaction-level suites.
