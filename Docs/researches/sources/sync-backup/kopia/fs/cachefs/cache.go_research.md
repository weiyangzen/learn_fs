<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/kopia/fs/cachefs/cache.go -->
# sources/sync-backup/kopia/fs/cachefs/cache.go

## Purpose
Implements an in-memory LRU-style cache for directory entry lists, keyed by object ID, to speed repeated filesystem traversal.

## Important APIs, Types, And Functions
Key types are `cacheEntry`, `Cache`, `Loader`, `EntryWrapper`, and `Options`. Important methods are `IterateEntries`, `getEntriesFromCacheLocked`, `getEntries`, `removeEntryLocked`, plus list helpers `moveToHead`, `addToHead`, and `remove`.

## Control Flow
`IterateEntries` caches only directories implementing `object.HasObjectID`; others use direct iteration. `getEntries` locks the cache, checks unexpired entries, loads raw entries on miss, wraps entries for storage, skips caching oversized directories, inserts at the head, and evicts tail entries until directory-count and total-entry limits are satisfied.

## State And Persistence Behavior
State is process-local memory: map of cache IDs to entry slices, total entry count, and doubly linked LRU list. Entries expire after 24 hours by default. There is no disk persistence.

## Dependencies And Integration Points
Integrates `fs.GetAllEntries`, object IDs, internal clock/logging, and wrappers from `cachefs.go`.

## Risks And Edge Cases
The function returns `raw` after inserting `wrapped`, so the first miss returns unwrapped entries while later hits return wrapped entries; this appears intentional or at least important to validate. The loader runs while holding the cache lock, limiting concurrency. Nil cache bypasses caching.

## Test Signals
Tests cover LRU ordering, size eviction, oversized non-caching, and lock release on error/hit/miss. Additional tests should cover wrapper behavior and expiration.
<!-- END_FILE_RESEARCH: sources/sync-backup/kopia/fs/cachefs/cache.go -->
