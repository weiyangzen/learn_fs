# sources/storage-engines/rocksdb/table/block_based/filter_block_reader_common.h

## Purpose
Declares `FilterBlockReaderCommon`, a templated base class that lets full and partitioned filter readers share table access, cached block ownership, range compatibility, and cache cleanup behavior while still exposing the `FilterBlockReader` interface.

## Important APIs, Types, And Functions
The constructor accepts a `BlockBasedTable` and movable `CachableEntry<TBlocklike>`, then records full-length prefix-extractor support. Public overrides are `RangeMayExist` and `EraseFromCacheBeforeDestruction`. Protected helpers include `ReadFilterBlock`, `table`, `table_prefix_extractor`, `whole_key_filtering`, `cache_filter_blocks`, `GetOrReadFilterBlock`, and `ApproximateFilterBlockMemoryUsage`.

## Control Flow
Derived readers call protected helpers when they need filter data. The base class decides whether to use an already held filter block or load it through the table/cache. For iterator range filtering, callers enter `RangeMayExist`, which performs prefix-domain and upper-bound checks before invoking derived `PrefixMayMatch`.

## State And Persistence Behavior
State is a non-owning table pointer, a `CachableEntry` that may own or reference a cached filter block, and prefix-extractor length flags. No durable table bytes are modified.

## Dependencies And Integration Points
Depends on `cachable_entry.h`, `filter_block.h`, `BlockBasedTable`, and `FilePrefetchBuffer`. It is the shared base for `FullFilterBlockReader` and partitioned filter readers using `Block_kFilterPartitionIndex`.

## Risks And Edge Cases
The constructor assumes the table and table representation are valid for the reader lifetime. Derived readers must not misuse `GetOrReadFilterBlock` after table teardown. Prefix full-length metadata is captured once, so it must match the immutable table prefix extractor.

## Test Signals
Coverage is indirect through readers that inherit it, especially cache pin/unpin behavior, prefix range pruning, and upper-bound compatibility tests.
