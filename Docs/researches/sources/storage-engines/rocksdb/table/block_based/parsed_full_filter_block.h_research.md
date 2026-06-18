# sources/storage-engines/rocksdb/table/block_based/parsed_full_filter_block.h

Purpose: declares the shareable/cacheable in-memory representation of a full filter block. It separates parsing and ownership of filter block contents from readers that execute membership tests.

Important APIs/types/functions: `ParsedFullFilterBlock` exposes `filter_bits_reader()`, `ApproximateMemoryUsage()`, `own_bytes()`, `ContentSlice()`, and typed cache constants `kCacheEntryRole = kFilterBlock` and `kBlockType = kFilter`. It owns a `BlockContents` and a `std::unique_ptr<FilterBitsReader>`.

Control flow: construction is in the `.cc`; after construction, readers only query accessors. `ApproximateMemoryUsage` delegates to the underlying `BlockContents` and explicitly does not include `FilterBitsReader` memory, as called out by TODO.

State and persistence: the persisted state is the raw filter block bytes in the SST. This class owns or references those bytes according to `BlockContents`, and holds transient parsed reader state for cache reuse. `ContentSlice()` lets typed cache infrastructure key or charge the raw content slice.

Dependencies/integration: depends on `BlockContents`, `BlockType`, and filter policy abstractions. It is used as `CachableEntry<ParsedFullFilterBlock>` in partitioned filters and likely full filters; the static role/type constants integrate with RocksDB block cache accounting.

Risks and test signals: memory accounting is incomplete for the reader object, which can understate pinned filter memory. Ownership mode matters because cached unowned values are exposed by `SetUnownedValue` in partitioned filter code. Direct tests are absent here, but `partitioned_filter_block_test.cc` creates `ParsedFullFilterBlock` instances for mocked filter partitions and validates filter behavior.
