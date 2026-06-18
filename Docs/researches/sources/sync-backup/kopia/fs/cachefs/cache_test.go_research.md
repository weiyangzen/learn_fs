<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/kopia/fs/cachefs/cache_test.go -->
# sources/sync-backup/kopia/fs/cachefs/cache_test.go

## Purpose
Unit tests for cachefs cache insertion, hits, LRU ordering, eviction by directory and entry limits, oversized directories, and lock release behavior.

## Important APIs, Types, And Functions
Defines helper types `cacheSource`, `cacheVerifier`, and `lockState`, plus `TestCache` and `TestCacheGetEntriesLocking`.

## Control Flow
`TestCache` creates fake entry lists of varying sizes, calls `getEntries`, verifies miss/hit counters, and checks LRU order and size invariants after each operation. The locking test swaps in a lock wrapper, forces a loader error, and verifies the cache is unlocked after errors and normal accesses.

## State And Persistence Behavior
State under test is the cache's internal map, total count, head/tail linked list, and lock counter.

## Dependencies And Integration Points
Integrates internal test logging, fake fs entries, maps cloning, and atomic lock-state tracking.

## Risks And Edge Cases
Tests intentionally inspect internals, so refactors of cache representation require test changes. They do not cover expiration timing or object-ID-based `IterateEntries` wrapping.

## Test Signals
Strong signal for eviction and deadlock regressions, especially the historic lock issues referenced by comments.
<!-- END_FILE_RESEARCH: sources/sync-backup/kopia/fs/cachefs/cache_test.go -->
