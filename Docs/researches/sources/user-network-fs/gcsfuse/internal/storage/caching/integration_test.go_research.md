# sources/user-network-fs/gcsfuse/internal/storage/caching/integration_test.go

## Purpose
`integration_test.go` verifies `FastStatBucket` behavior with a real in-memory stat cache and a fake bucket rather than strict mocks. It checks observable caching semantics across object create, stat, list, update, positive TTL expiration, negative TTL expiration, and negative-cache invalidation.

## Important APIs, Types, and Functions
`IntegrationTest.SetUp` creates an LRU cache sized with `cfg.AverageSizeOfPositiveStatCacheEntry`, wraps it with `metadata.NewStatCacheBucketView`, constructs `fake.NewFakeBucket`, and wraps the fake bucket with `caching.NewFastStatBucket`. The helper `stat` calls `bucket.StatObject` and converts the returned `MinObject` to a full object with `storageutil.ConvertMinObjectToObject`.

## Control Flow
Each test performs operations through both the caching bucket and the wrapped fake bucket. Back-door operations against `t.wrapped` simulate GCS changing outside the cache wrapper. Positive-cache tests create, stat, list, or update through the cache wrapper, delete the real object through the back door, then verify stat still returns the cached object until TTL expiry. Negative-cache tests stat a missing object to cache not-found, create the object through the back door, then verify the object remains hidden until a cache invalidating operation or negative TTL expiry occurs.

## State and Persistence Behavior
All state is in-memory: the fake bucket owns object records and the LRU-backed stat cache owns cached metadata. A simulated clock controls both primary and negative TTL checks. The tests intentionally separate cache state from underlying bucket state to prove staleness is allowed within configured TTL windows.

## Dependencies and Integration Points
The file integrates `cfg`, `cache/lru`, `cache/metadata`, `caching`, `fake`, `gcs`, `storageutil`, ogletest matchers, and `timeutil.SimulatedClock`. It is the bridge between unit-level interaction tests and the actual metadata cache implementation.

## Risks and Edge Cases
The tests encode the intended staleness contract: cache may return deleted objects until positive TTL expiry and may hide newly created objects until negative TTL expiry unless a wrapper-observed create/list/update invalidates the entry. If product expectations change toward stronger consistency, these tests will need revision. They do not cover HNS folder cache behavior or cancelled contexts; those are in `fast_stat_bucket_test.go`.

## Test Signals
Coverage includes positive insertion from create/stat/list/update, positive expiration, negative insertion from stat not-found, create/list/update invalidating negative entries, and negative expiration. Because it uses real cache and fake bucket implementations, it catches integration mistakes that pure oglemock call-order tests can miss.
