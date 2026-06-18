# sources/storage-engines/rocksdb/table/block_based/full_filter_block.cc

## Purpose
Implements full-table filter block building and reading for block-based tables. A full filter contains one filter over all keys and/or prefixes in the SST file and is used to avoid unnecessary data-block reads.

## Important APIs, Types, And Functions
`FullFilterBlockBuilder` implements `EstimateEntriesAdded`, `OnDataBlockFinalized`, `CurrentFilterSizeEstimate`, `UpdateFilterSizeEstimate`, `AddWithPrevKey`, `Add`, and `Finish`. `FullFilterBlockReader` implements `Create`, `KeyMayMatch`, `PrefixMayMatch`, `KeysMayMatch`, `PrefixesMayMatch`, private single and batch `MayMatch`, and `ApproximateMemoryUsage`.

## Control Flow
The builder receives user keys without timestamps. If a prefix extractor exists and accepts the key, it adds the prefix and optionally the whole key through `AddKeyAndAlt`; otherwise it adds only the whole key when whole-key filtering is enabled. `Finish` delegates to the configured `FilterBitsBuilder` and returns its status. The reader creation path can prefetch or pin the parsed full filter, or create a lazy reader that loads the block from cache/table on first use. Query paths call `GetOrReadFilterBlock`, obtain the `FilterBitsReader`, then update bloom hit/miss counters and prune keys/ranges on false.

## State And Persistence Behavior
Persistent bytes are whatever the selected `FilterBitsBuilder` returns for the full filter block. Runtime builder state includes a `FilterBitsBuilder`, optional owned filter bytes, and a cached size estimate. Reader state is inherited from `FilterBlockReaderCommon` and may own, pin, or lazily read a `ParsedFullFilterBlock`.

## Dependencies And Integration Points
Depends on `FilterBitsBuilder`, `FilterBitsReader`, `ParsedFullFilterBlock`, `BlockBasedTable::RetrieveBlock`, perf counters, prefix extractors, cache entries, and read options. It is used by block-based table builders/readers when partitioned filters are not selected.

## Risks And Edge Cases
Read errors and missing filter readers must return maybe-present to avoid false negatives. Empty full filters keep legacy semantics where `KeyMayMatch` can return true at the block-reader layer. Batch filtering must keep arrays aligned with the filtered `MultiGetRange`, especially when some keys are outside the prefix extractor domain.

## Test Signals
`full_filter_block_test.cc` verifies empty builders, plugin filter support, duplicate collapse, entry estimates, single-key lookup, and negative filtering for missing keys.
