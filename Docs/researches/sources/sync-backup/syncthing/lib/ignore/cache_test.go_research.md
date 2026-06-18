# sources/sync-backup/syncthing/lib/ignore/cache_test.go

## Purpose
Tests ignore cache storage, retrieval, access-time refresh, and expiration.

## Important APIs, Types, and Functions
`TestCache` and `fakeClock`.

## Control Flow
The test replaces package `clock`, creates a cache, checks a miss, stores ignored/deletable and not-ignored results, verifies both hit, advances fake time, accesses one key to refresh it, cleans with a duration threshold, then asserts only the stale key was removed.

## State and Persistence Behavior
Mutates package-level `clock` temporarily and restores it with defer. Cache state is in-memory.

## Dependencies and Integration Points
Uses `ignoreresult` flags and `cache` internals from the same package.

## Risks
Because `cache.set` uses real `time.Now`, correctness relies on subsequent fake-clock `get` calls to refresh entries before expiration checks.

## Test Signals
Good basic signal that cached ignore decisions can expire without evicting recently accessed entries.
