# sources/user-network-fs/gcsfuse/internal/storage/caching/fast_stat_bucket_test.go

## Purpose
`fast_stat_bucket_test.go` is the main unit-test suite for the caching `FastStatBucket` wrapper. It verifies that the wrapper uses `metadata.StatCache` as a positive and negative metadata cache while delegating actual object and folder operations to an underlying `gcs.Bucket`.

## Important APIs, Types, and Functions
The shared fixture `fastStatBucketTest` constructs a simulated clock, `mock_gcscaching.MockStatCache`, mocked wrapped bucket, and `caching.NewFastStatBucket(primaryCacheTTL, cache, clock, wrapped, negativeCacheTTL, isTypeCacheDeprecated, isImplicitDir)`. Test suites cover object creation, resumable and appendable writers, upload finalization, pending-write flush, copy, compose, stat, list, update, delete, folder APIs, move, reader construction, and multi-range downloader construction.

The stat-related tests exercise `gcs.StatObjectRequest` fields including `ForceFetchFromGcs`, `ReturnExtendedObjectAttributes`, and `FetchOnlyFromCache`. Folder tests exercise `GetFolderRequest.FetchOnlyFromCache`. Listing tests validate cache insertion for `MinObjects`, collapsed runs, implicit directories, and hierarchical namespace buckets.

## Control Flow
Mutation operations generally expect cache invalidation before calling the wrapped bucket. `CreateObject`, `FinalizeUpload`, `FlushPendingWrites`, `CopyObject`, `ComposeObjects`, `UpdateObject`, `CreateFolder`, `RenameFolder`, and `MoveObject` erase stale entries, delegate, and insert successful returned metadata into cache with `clock.Now().Add(primaryCacheTTL)`. Failure paths usually return the wrapped error without positive insertion; precondition and not-found paths are checked so stale entries are not retained incorrectly.

`StatObject` first consults `LookUp` unless `ForceFetchFromGcs` bypasses the cache. A positive hit returns the cached `MinObject`, a cached nil means a negative hit and returns `gcs.NotFoundError`, and a miss delegates to the wrapped bucket. Wrapped not-found responses add a negative cache entry expiring at `negativeCacheTTL`; wrapped success inserts a positive entry. The test also asserts that requesting extended attributes without forcing a GCS fetch panics, because the cache cannot supply the extended attribute surface.

`ListObjects` delegates first, then inserts listed objects and derived directory entries unless the context has already been cancelled. Flat buckets cache implicit directories from prefixes, object paths, and collapsed runs when implicit-dir caching is enabled. HNS buckets cache real folder entries differently, using `InsertFolder` for collapsed folder results. Reader and multi-range downloader creation do not use cache for success, but a wrapped `NotFoundError` erases the object entry to remove stale positive metadata.

## State and Persistence Behavior
The tests are memory-only but model time-based cache state with `timeutil.SimulatedClock`. They assert expiration timestamps rather than sleeping. The wrapper state under test is the stat cache: object positive entries, object negative entries, folder positive entries, folder negative entries, implicit directory entries, and prefix-wide erasure for folder rename. There is no durable persistence in this file.

## Dependencies and Integration Points
The file depends on `caching.NewFastStatBucket`, `metadata.StatCache` through a generated oglemock mock, the storage `MockBucket`, `gcs` request/response types, `storage.ObjectWriter`, `fake.FakeReader`, and ogletest/oglemock matchers. It integrates indirectly with the cache implementation by treating `StatCache` as an interaction contract.

## Risks and Edge Cases
The highest-risk areas are invalidation ordering around mutations, negative-cache invalidation after create/list/update, and not caching partial/list results when context cancellation is already visible. Extended object attributes are deliberately unavailable from cache; code paths that set `ReturnExtendedObjectAttributes` without `ForceFetchFromGcs` are expected to panic. HNS folder entries and flat implicit directories have different cache insertion semantics, so regressions can appear only for one bucket type.

## Test Signals
This file itself is a broad test signal. It covers happy paths and failures for wrapped bucket calls, TTL computation, positive/negative object cache hits, cache-only stat/folder misses returning `caching.CacheMissError`, folder CRUD caching, move invalidation of both source and destination, reader/downloader stale-cache removal on not-found, and cancelled-listing suppression of cache updates.
