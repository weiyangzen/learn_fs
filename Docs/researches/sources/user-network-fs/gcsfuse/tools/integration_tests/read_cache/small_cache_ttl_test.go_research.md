# sources/user-network-fs/gcsfuse/tools/integration_tests/read_cache/small_cache_ttl_test.go

## Purpose

`small_cache_ttl_test.go` validates file-cache behavior when metadata cache TTL is finite and the file-cache capacity is small. It verifies both stale-cache serving before metadata expiry and cache hits after metadata refresh when object content has not changed.

## Important APIs, Types, and Functions

`smallCacheTTLTest` is a `testify/suite` suite with per-run flags, storage client, context, and base test name. `SetupSuite` configures log/cache paths and mounts GCSFuse; `SetupTest` truncates logs, removes the cache directory, and creates a fresh test prefix; `TearDownTest` preserves logs on failure; `TearDownSuite` unmounts. `TestReadAfterUpdateAndCacheExpiryIsCacheMiss` and `TestReadForLowMetaDataCacheTTLIsCacheHit` are the behavioral tests. `TestSmallCacheTTLTest` expands config-derived flag sets and runs the suite.

## Control Flow

The update/expiry test uses `operations.RetryUntil` to keep the first read, direct GCS object modification, and immediate second read within the configured metadata TTL. It expects the second read to serve stale cached content, then sleeps for TTL expiry and expects a third read to miss cache and fetch the smaller updated object. The low-TTL cache-hit test reads an object, waits past metadata TTL, reads again, and immediately reads a third time; unchanged content should remain cache-hit eligible.

## State and Persistence Behavior

Each test creates objects in a unique GCS prefix, writes file-cache content to `testEnv.cacheDirPath`, and appends structured read logs to `testEnv.cfg.LogFile`. The first test changes remote object content through the storage client while local cache state persists across reads. Cache validation reads local cache file sizes and JSON log entries.

## Dependencies and Integration Points

The suite relies on shared read-cache helpers (`setupFileInTestDir`, `modifyFile`, `readFileAndValidateCacheWithGCS`, `readFileAndGetExpectedOutcome`, `validate`, and cache-size validators), the JSON read-log parser, `operations.RetryUntil`, and suite flag matrices from `setup_test.go`.

## Risks and Edge Cases

The first scenario is timing-sensitive: if object creation, read, modification, and second read exceed `metadataCacheTTlInSec`, stale serving is no longer expected, so the retry wrapper restarts setup. Log assertions require exactly three structured read logs, so unrelated reads from setup or kernel behavior can break the signal. Cache size expectations depend on configured file sizes and chunk counts.

## Test Signals

Expected logs are miss, hit, miss for the update/expiry path and miss, hit, hit for the unchanged-content path. Content comparison must show stale data before TTL expiry and updated data after expiry. The suite should pass with both serial and parallel downloads, and with HTTP or gRPC client protocol flag variants.
