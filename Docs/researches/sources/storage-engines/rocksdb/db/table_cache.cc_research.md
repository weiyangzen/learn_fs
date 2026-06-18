# sources/storage-engines/rocksdb/db/table_cache.cc

## Purpose

`table_cache.cc` implements the column-family table reader cache. It opens SST files, constructs `TableReader`s through the configured table factory, caches or pins readers, serves point and batched reads, manages row-cache replay logs, exposes table properties and approximate size/offset helpers, and marks obsolete table readers.

## Important APIs, Types, and Functions

Core functions are `GetTableReader`, `FindTable`, `NewIterator`, `Get`, `MultiGetFilter`, generated sync/async `MultiGet`, `GetRangeTombstoneIterator`, `GetTableProperties`, `ApproximateKeyAnchors`, `GetMemoryUsageByTableReader`, `ApproximateOffsetOf`, `ApproximateSize`, `Evict`, `Lookup`, and `ReleaseObsolete`. Private helpers build row-cache prefixes and replay row-cache hits. `kLoadConcurency` stripes loader mutexes to limit duplicate opens.

## Control Flow

`FindTable` first honors explicitly requested ephemeral readers, then pinned file readers, then cache lookup, then serialized file open under a stripe mutex. It rechecks pinned/cache state under the mutex before opening and can pin handles into file metadata when the cache capacity indicates effectively infinite open files. `NewIterator` uses `FindTable`, applies optional table filters, registers cache-handle cleanup on iterators, wires range tombstones into an aggregator or truncated iterator, and transfers ephemeral reader ownership to iterator cleanup only after all setup succeeds. `Get` and `MultiGet` check row cache when safe, open or find the table reader, update range tombstone sequence numbers, invoke table-reader lookup, and insert replay logs back into row cache on hits.

## State and Persistence Behavior

The cache key is the file number bytes and is shared with blob cache infrastructure. Persistent data is not written here, but file open metadata can be passed to the filesystem for fast SST open and refreshed into manifest-facing metadata. Row cache entries include row-cache id, file number, and a visibility sequence discriminator so snapshot reads do not reuse unsafe entries. Obsolete release marks readers obsolete and erases cache entries after file deletion decisions elsewhere.

## Dependencies and Integration Points

Dependencies include file readers, `TableReader`, table factories, `VersionEdit` metadata, range tombstone iterators, block cache tracing, IO tracing, statistics, sync points, and coroutine macros. `VersionBuilder`, `VersionStorageInfo`, read paths, compaction iterators, and DB property APIs use this class as the shared SST access layer.

## Risks and Test Signals

Risks include leaked cache handles, double-free around ephemeral readers, no-IO reads accidentally doing I/O, stale fast-open metadata, unsafe row-cache keys for snapshot/callback reads, missed range tombstone updates, and races between pinning and cache lookup. Tests should cover cache hit/miss/open errors, `kBlockCacheTier` incomplete behavior, row cache replay, MultiGet with filters and tombstones, iterator cleanup, ephemeral-reader bypass, fast-SST metadata size limits, obsolete release, and concurrent opens of the same file.
