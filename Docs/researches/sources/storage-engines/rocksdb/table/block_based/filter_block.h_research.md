# sources/storage-engines/rocksdb/table/block_based/filter_block.h

## Purpose
Declares the abstract filter block builder and reader interfaces used by block-based tables. It provides a common contract for full filters, partitioned filters, plugin filter policies, point lookups, prefix checks, multi-get pruning, range existence checks, memory accounting, and cache lifecycle hooks.

## Important APIs, Types, And Functions
`FilterBlockBuilder` defines `Add`, `AddWithPrevKey`, `IsEmpty`, `EstimateEntriesAdded`, `CurrentFilterSizeEstimate`, `OnDataBlockFinalized`, `PrevKeyBeforeFinish`, `Finish`, `ResetFilterBitsBuilder`, and `MaybePostVerifyFilter`. `FilterBlockReader` defines `KeyMayMatch`, `KeysMayMatch`, `PrefixMayMatch`, `PrefixesMayMatch`, `ApproximateMemoryUsage`, `ToString`, `CacheDependencies`, `EraseFromCacheBeforeDestruction`, and `RangeMayExist`. `MultiGetRange` aliases `MultiGetContext::Range`.

## Control Flow
Table builders feed keys without timestamps into a concrete builder, optionally with previous-key context for partitioned range logic, then repeatedly call `Finish` until a full or partitioned filter is complete. Readers answer maybe-match queries: the base multi-get helpers loop through a range and call single-key methods, skipping keys when filters return false.

## State And Persistence Behavior
This header defines interfaces, not concrete storage. The `Finish` contract specifies ownership and lifetime of returned filter bytes, including optional transfer through `filter_owner`, and supports partitioned filters through `Status::Incomplete` plus the last partition block handle.

## Dependencies And Integration Points
Integrates with `FilterPolicy`, `GetContext`, `ReadOptions`, `BlockCacheLookupContext`, `FilePrefetchBuffer`, `SliceTransform`, `Comparator`, `BlockHandle`, and `MultiGetContext`. It is consumed by full-filter, partitioned-filter, and table-reader code.

## Risks And Edge Cases
Implementations must preserve no-false-negative semantics: read failures, missing filters, or unsupported filter formats should generally return maybe-present. `AddWithPrevKey` introduces sequencing constraints, and callers using it must call `PrevKeyBeforeFinish` when required. Multi-get skipping depends on safe iterator mutation through `MultiGetRange::SkipKey`.

## Test Signals
Signals come through full-filter and partitioned-filter tests, multi-get filter pruning, cache dependency tests, and table-reader point/range lookup behavior.
