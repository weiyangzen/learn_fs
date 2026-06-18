# sources/storage-engines/rocksdb/db/table_cache_sync_and_async.h

## Purpose

`table_cache_sync_and_async.h` contains the macro-expanded implementation of `TableCache::MultiGet` for both ordinary and coroutine builds. It is included twice by `table_cache.cc` with different macro definitions so RocksDB can compile sync and async variants from one body.

## Important APIs, Types, and Functions

The file defines `DEFINE_SYNC_AND_ASYNC(Status, TableCache::MultiGet)` with parameters for read options, comparator, file metadata, `MultiGetContext::Range`, mutable CF options, file read histogram, filter/range-deletion skips, level, and an optional existing table handle. It uses coroutine macros `CO_AWAIT` and `CO_RETURN` when enabled.

## Control Flow

The function starts with a pinned reader or optional handle. It builds a `MultiGetRange`, checks row cache when enabled and sequence numbers are not needed, skips keys satisfied from row cache, then opens/finds the table if remaining keys need table access. It updates range tombstone sequence numbers unless disabled, delegates to `TableReader::MultiGet`, and maps `kBlockCacheTier` incomplete table-cache misses into `MarkKeyMayExist` results. After table lookup it records replay logs into row cache for keys that produced cacheable data and releases any table handle it owns.

## State and Persistence Behavior

State is transient except row-cache insertions. Replay logs are temporarily attached to each `GetContext` and are detached before insertion. Row-cache charges include string capacity plus object overhead. The function does not write SST/WAL data, but its row-cache and range-tombstone updates affect read results and performance.

## Dependencies and Integration Points

It depends on `util/coro_utils.h`, the declarations in `table_cache.h`, `GetContext`, `MultiGetContext`, row cache helpers, table readers, and range tombstone iterators. It is part of point-lookup batching used by DB read paths.

## Risks and Test Signals

Risks include row-cache entry index mismatches after skipped keys, leaked handles across coroutine suspension, replay logs left attached on errors, and inconsistent no-IO behavior versus single-key `Get`. Tests should cover all-row-cache hits, mixed hits/misses, row-cache disabled by sequence reads, range tombstone updates, filter skipping, existing handle ownership, pinned-reader use, and both sync and coroutine compilation paths.
