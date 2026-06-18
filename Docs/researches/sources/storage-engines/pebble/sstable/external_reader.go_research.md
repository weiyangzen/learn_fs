# sources/storage-engines/pebble/sstable/external_reader.go

## Purpose
Provides public shims for callers using `sstable.NewReader` directly to configure and evict block cache entries without reaching into internal packages.

## Important APIs, Types, and Functions
- `CacheHandle` aliases `cache.Handle`.
- `SetCacheOptions` sets `ReaderOptions.CacheOpts` from a cache handle and caller-assigned file number.
- `CacheHandleEvictFile` evicts all cached blocks for a file number.

## Control Flow
`SetCacheOptions` writes `sstableinternal.CacheOptions` into the supplied options. `CacheHandleEvictFile` delegates to the cache handle’s file eviction method.

## State and Persistence Behavior
No SSTable bytes are changed. State affected is reader cache configuration and cache contents. File numbers are caller-assigned and must be unique within the cache handle namespace.

## Dependencies and Integration Points
Bridges public `sstable` users to `internal/cache` and `internal/sstableinternal` cache options. Normal Pebble DB usage does not need this file because Pebble manages cache options internally.

## Risks and Edge Cases
Cache key collisions are possible if external callers reuse file numbers incorrectly. The helpers expose cache configuration but not lifecycle management beyond eviction.

## Test Signals
No direct tests in this subset; indirectly covered by reader tests that configure `CacheOpts`.
