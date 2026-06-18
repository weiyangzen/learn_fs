# sources/storage-engines/rocksdb/table/block_based/block_based_table_reader.h

## Purpose
Declares the `BlockBasedTable` `TableReader` implementation and the shared helper surface for RocksDB's block-based SST reader. The header defines the public table-reader API, cache and block retrieval helpers, index-reader abstraction, metadata prefetch hooks, checksum and dumping hooks, read-scoped buffer helper declarations, and the `Rep` state container used by the implementation and closely coupled block-based reader components.

## Important APIs, Types, And Functions
The free helper declarations cover read-scoped allocation and cache policy: `AllocateReadScopedBlockBuffer`, `AllocateReadScopedAlignedBuffer`, `MakeReadScopedAlignedBufferAllocator`, `GetReadScopedBlockBufferProvider`, `ShouldUseDataBlockCacheForIterator`, `CopyBufferToHeapBlockContents`, and `CopyBufferToReadScopedBlockContents`.

`BlockBasedTable` exports `Open`, `PrefixRangeMayMatch`, `NewIterator`, `NewRangeTombstoneIterator`, `Get`, `MultiGetFilter`, sync and async `MultiGet`, `Prefetch`, approximate offset/size/key-anchor APIs, cache probes and erasure helpers, compaction setup, table properties access, sequence-to-time mapping access, memory usage, table dumping, checksum verification, and obsolete marking.

The nested `IndexReader` interface abstracts binary-search, hash, partitioned, and user-defined index readers through `NewIterator`, `ApproximateMemoryUsage`, `CacheDependencies`, and `EraseFromCacheBeforeDestruction`. Private templates declare `LookupAndPinBlocksInCache`, `CreateAndPinBlockInCache`, `NewDataBlockIterator`, `MaybeReadBlockAndLoadToCache`, `RetrieveBlock`, `SaveLookupContextOrTraceRecord`, `GetDataBlockFromCache`, and `PutDataBlockToCache`.

`PartitionedIndexIteratorState` adapts partitioned-index block maps into `TwoLevelIteratorState`. `Rep` stores immutable table reader state: options, file, cache keys, footer, metadata readers, filter/dictionary/index handles, table properties, sequence mapping, index encoding flags, range tombstones, decompressor, restart intervals, separated key/value mode, checksum-open marker, timestamp persistence flag, filesystem prefetch support, obsolete-cache aggressiveness, cache reservation handle, and optional user-defined-index block.

## Control Flow
The header establishes the layering: external callers use `TableReader` virtual methods, the implementation routes metadata access through `IndexReader` and `FilterBlockReader`, and block materialization flows through typed `CachableEntry` templates. `DECLARE_SYNC_AND_ASYNC_OVERRIDE` and `DECLARE_SYNC_AND_ASYNC_CONST` declare paired sync/coroutine versions of `MultiGet` and `RetrieveMultipleBlocks`; the implementation header is included with different coroutine macros to generate both variants.

Index lookup starts with `NewIndexIterator`, then data-block conversion is done by `NewDataBlockIterator`. Cache decisions are centralized through `RetrieveBlock`, `MaybeReadBlockAndLoadToCache`, and typed block cache helpers. Open-time construction flows through `PrefetchTail`, `ReadMetaIndexBlock`, `ReadPropertiesBlock`, `ReadRangeDelBlock`, `PrefetchIndexAndFilterBlocks`, `CreateIndexReader`, and `CreateFilterBlockReader`.

## State And Persistence Behavior
The header is declarative, but it documents the state that persists for a table reader lifetime. `Rep` holds a moved-in random access file, table metadata, constructed readers, cache identity, timestamp and global sequence settings, and ownership handles for cache reservation and user-defined-index data. It does not declare any mutation of the SST itself. Cache persistence is external to the table reader and keyed through `base_cache_key` plus block offsets.

`Rep::get_global_seqno` disables global sequence numbers for filter partition index and compression dictionary blocks. `CreateFilePrefetchBuffer` and `CreateFilePrefetchBufferIfNotExists` centralize per-reader file prefetch buffer construction. `uncache_aggressiveness` is an atomic marker used later during destruction to evict cached blocks for obsolete files.

## Dependencies And Integration Points
The declarations tie together RocksDB cache roles and keys, block cache interfaces, range tombstone fragmenters, sequence-to-time mappings, table properties, block-based table options, filters, uncompression dictionaries, persistent cache, table format, two-level iterators, block cache tracing, aligned buffers, coroutine utilities, and hash containers.

Other block-based table files depend on this header for template methods and `Rep` details. Table cache, table factory, iterators, filter readers, partitioned index readers, user-defined index wrappers, compaction code, SST dump tooling, and tests all integrate through the API declared here.

## Risks And Edge Cases
The header exposes many implementation details for template and friend access, so changes to `Rep`, block type mapping, or template signatures can break distant block-based components. `ReadOptions` lifetime is explicitly required to outlive iterators. The `IndexReader::NewIterator` contract allows returning a different iterator than the caller supplied, so callers must preserve both ownership and stack lifetime correctly.

Cache key setup depends on table properties for stable identity and falls back to current DB session and file number for older files. The `BlockSizeWithTrailer` and compression-type helpers assume block-based serialized contents with the expected trailer. User-defined timestamps can be absent in persisted keys even when the active comparator has timestamp size, so parsing code must consult `user_defined_timestamps_persisted`.

## Test Signals
Tests that instantiate `BlockBasedTable` and exercise the declared APIs are concentrated in `table/block_based/block_based_table_reader_test.cc`, with parameterization over compression, index type, cache presence, direct reads, async I/O, timestamps, and block alignment. Cache-specific APIs are indirectly covered by cache and tiered-cache tests. Public `TableReader` methods are also exercised by DB read, iterator, compaction, checksum, SST dump, and fuzz tests.
