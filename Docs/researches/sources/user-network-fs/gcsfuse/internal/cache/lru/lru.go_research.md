<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/gcsfuse/internal/cache/lru/lru.go -->
# sources/user-network-fs/gcsfuse/internal/cache/lru/lru.go

## Purpose
This file implements a generic size-bounded LRU cache keyed by strings and storing values that implement `ValueType.Size() uint64`. It is used by file-cache metadata and stat cache code to bound memory or disk-accounting state and to drive eviction callbacks at higher layers.

## Important APIs and types
`Cache` stores `maxSize`, `currentSize`, a most-recent-first linked list, and a key-to-element index guarded by `locker.RWLocker`. Public APIs are `NewCache`, `Insert`, `Erase`, `LookUp`, `LookUpWithoutChangingOrder`, `UpdateWithoutChangingOrder`, `UpdateSize`, and `EraseEntriesWithGivenPrefix`. Error sentinels include invalid entry, oversized entry, invalid update size, and missing entry.

## Control flow and state behavior
`Insert` rejects nil or oversized values, updates existing entries while moving them to the front, adds new entries at the front, then evicts from the tail until `currentSize <= maxSize`, returning evicted values to the caller. `LookUp` moves entries to front; `LookUpWithoutChangingOrder` uses a read lock and preserves recency. `UpdateWithoutChangingOrder` replaces a value only if the key exists and size is unchanged. `EraseEntriesWithGivenPrefix` snapshots matching keys under read lock, then deletes them under write lock.

## State and persistence behavior
The cache is in-memory only. Its evicted values are returned so callers can perform external cleanup, such as invalidating download jobs and removing cache files. `UpdateSize` increments `currentSize` without changing the stored value or evicting immediately; this is intentionally used by sparse files whose downloaded byte count grows incrementally, but it can temporarily violate the invariant until future inserts trigger eviction.

## Dependencies and integration points
The cache depends on `container/list`, reflection-based invariant checks, strings prefix matching, and gcsfuse's locker package. File cache uses it for `data.FileInfo`; metadata stat cache uses it for stat entries; sparse downloader uses `UpdateSize`.

## Risks and edge cases
`NewCache` does not validate `maxSize`; invariant checks catch zero only when enabled. `UpdateSize` can make `currentSize > maxSize`, despite the invariant comment, so invariant checking during sparse size updates may be risky if enabled around that path. Prefix erasure is O(number of entries) and can be costly for large caches, hence benchmarks.

## Test signals
`lru_test.go` covers insert, overwrite, eviction ordering, multiple eviction, erase, prefix erase, update-without-order, lookup-without-order, and concurrent operations. Benchmarks cover insert, lookup, erase, mixed concurrency, million-entry insertion, and million-entry prefix deletion.
<!-- END_FILE_RESEARCH: sources/user-network-fs/gcsfuse/internal/cache/lru/lru.go -->
