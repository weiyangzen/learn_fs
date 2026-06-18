# sources/sync-backup/syncthing/lib/ignore/cache.go

## Purpose
Provides a small match-result cache for ignore matching with access-time based cleanup.

## Important APIs, Types, and Functions
`nower`, package variable `clock`, `cache`, `cacheEntry`, `newCache`, `clean`, `get`, `set`, `len`, and `defaultClock`.

## Control Flow
`get` returns a cached `ignoreresult.R` and refreshes its access time. `set` stores the result with current time. `clean` deletes entries whose last access exceeds the supplied duration.

## State and Persistence Behavior
In-memory map only. Access timestamps are Unix nanoseconds.

## Dependencies and Integration Points
Used by `ignore.Matcher` when `WithCache(true)` is enabled. `clock` is replaceable in tests.

## Risks
The cache is not internally synchronized; callers must hold `Matcher`'s mutex. `set` uses `time.Now()` directly instead of the injectable `clock`, while tests mainly rely on later `get` refreshing via fake time.

## Test Signals
`cache_test.go` verifies hits, false-result caching, access refresh, and cleanup.
