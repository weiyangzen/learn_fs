## sources/sync-backup/syncthing/lib/discover/cache.go

Purpose: Provides cache primitives and metadata for discovery finders.

Important APIs/types/functions: `cachedFinder` wraps a `Finder` with positive/negative cache durations, per-finder `cache`, and optional suture token. `cachedError` can override negative cache time. `cache` exposes `Set`, `Get`, and `Cache`.

Control flow: Methods lock a mutex for map access; `Cache` returns a shallow copy of the map for safe iteration by callers.

State and persistence: In-memory map keyed by `protocol.DeviceID` to `CacheEntry`. No disk persistence.

Dependencies and integration points: Used by discovery manager to cache global lookup successes/failures and to aggregate local finder caches.

Risks: `Cache` returns `CacheEntry` values whose `Addresses` slices are not deep-copied. Callers should not mutate returned slices.

Test signals: `cache_test.go` exercises manager lookup cache aggregation and nonblocking child error access during slow lookups.
