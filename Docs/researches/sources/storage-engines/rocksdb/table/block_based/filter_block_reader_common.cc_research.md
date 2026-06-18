# sources/storage-engines/rocksdb/table/block_based/filter_block_reader_common.cc

## Purpose
Implements common cache-aware logic shared by full and partitioned filter block readers. It centralizes reading filter blocks, accessing table filter options, range-prefix compatibility checks, memory accounting, and cache eviction before destruction.

## Important APIs, Types, And Functions
Template methods include `ReadFilterBlock`, `table_prefix_extractor`, `whole_key_filtering`, `cache_filter_blocks`, `GetOrReadFilterBlock`, `ApproximateFilterBlockMemoryUsage`, `RangeMayExist`, `IsFilterCompatible`, and `EraseFromCacheBeforeDestruction`. The file explicitly instantiates the template for `Block_kFilterPartitionIndex` and `ParsedFullFilterBlock`.

## Control Flow
`GetOrReadFilterBlock` first reuses a pinned/owned `filter_block_` when present; otherwise it calls `ReadFilterBlock`, which delegates to `BlockBasedTable::RetrieveBlock` using the table's filter handle. `RangeMayExist` uses the caller's prefix extractor to transform the queried user key, checks upper-bound compatibility when requested, and delegates to `PrefixMayMatch` only when the entire iterator range can be safely represented by the same prefix.

## State And Persistence Behavior
The class does not persist data. It manages ownership or cache references through `CachableEntry<TBlocklike>` and can erase a cached filter block when `uncache_aggressiveness` is positive. Prefix extractor full-length metadata is cached at construction time in the header-side object.

## Dependencies And Integration Points
Depends on `BlockBasedTable`, `RetrieveBlock`, perf timers, block cache lookup context, `ParsedFullFilterBlock`, and prefix comparator APIs including timestamp-aware `CompareWithoutTimestamp` and `IsSameLengthImmediateSuccessor`. Full-filter and partitioned-filter readers inherit this behavior.

## Risks And Edge Cases
Upper-bound compatibility is subtle: using a prefix filter for a range whose upper bound crosses into another prefix would cause false negatives, so the code falls back to maybe-present. Read errors also fall back to maybe-present through callers. Cache erasure must distinguish entries owned by the reader versus entries only present in the table cache.

## Test Signals
Indirectly covered by full-filter, partitioned-filter, iterator upper-bound, cache pinning, and table-reader prefix seek tests. Perf counters around filter-block reads can reveal cache or IO regressions.
