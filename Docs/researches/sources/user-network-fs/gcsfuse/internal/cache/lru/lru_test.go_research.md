<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/gcsfuse/internal/cache/lru/lru_test.go -->
# sources/user-network-fs/gcsfuse/internal/cache/lru/lru_test.go

## Purpose
This ogletest suite validates correctness and concurrency behavior of the generic LRU cache. It verifies cache capacity enforcement, recency ordering, update semantics, prefix erasure, and thread safety under mixed operations.

## Important fixtures and APIs
`CacheTest` creates a `lru.Cache` with `MaxSize=50` and enables invariant checks. `testData` implements `ValueType` with a configurable `DataSize`. `insertAndAssert` centralizes insertion, expected evicted values, and expected error checks.

## Control flow and state behavior
Tests cover empty lookup, nil insert rejection, unknown lookup, filling to capacity, least-recently-used eviction after lookup changes recency, overwriting existing entries, multiple eviction for a large insert, rejecting values larger than max size, erasing present and absent keys, and prefix erasure. Update tests verify `UpdateWithoutChangingOrder` succeeds for same-size values, fails for missing keys or size changes, and does not move an entry to the front. Lookup-without-order tests prove read-only lookup also preserves eviction order.

## Dependencies and integration points
The suite imports `locker.EnableInvariantsCheck`, which makes internal list/index/current-size invariants active around lock operations. It uses Go `sync` and `math/rand` for concurrent tests. Prefix erasure tests reflect stat-cache and file-cache invalidation use cases.

## Risks and edge cases
`TestRaceCondition` is explicitly useful under `go test -race`; without race detector it mainly checks that operations complete. Concurrent prefix erasure only verifies no panic/race-like failure, not exact postcondition counts. Tests predate `UpdateSize`, so the sparse-size accounting API lacks direct unit coverage here.

## Test signals
The file gives strong correctness signals for LRU ordering, eviction return values, size validation, order-preserving update/lookup APIs used by downloader progress, prefix deletion, and coarse concurrent safety.
<!-- END_FILE_RESEARCH: sources/user-network-fs/gcsfuse/internal/cache/lru/lru_test.go -->
