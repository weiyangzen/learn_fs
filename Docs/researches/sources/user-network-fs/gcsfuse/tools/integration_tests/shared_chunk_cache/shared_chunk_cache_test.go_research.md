# sources/user-network-fs/gcsfuse/tools/integration_tests/shared_chunk_cache/shared_chunk_cache_test.go

## Purpose

This suite validates experimental shared chunk cache behavior for one or two GCSFuse mounts. It checks that a partial read caches a full chunk, that a second mount can reuse the cached chunk without rewriting cache files, and that a single mount gets cache hits on repeated reads.

## Important APIs, Types, and Functions

`mountPoint` records root, mount, test directory, and log paths. `BaseSuite` stores primary/secondary flags, mount points, and shared cache directory. `SharedChunkCacheTestSuite` embeds it. `SetupTest` prepares cache state and mounts primary/secondary GCSFuse instances in GCE mode or records pre-mounted GKE paths. `TearDownTest` saves logs on failure, unmounts/cleans mounts, and removes the shared cache directory. Helpers include `setupTestDir`, `mountGcsfuse`, `unmountAndCleanupMount`, `createTestFile`, `getCachedChunkCount`, and `getCacheFileModTimes`. Tests are `TestCacheMiss`, `TestCacheHit`, and `TestCacheHitSingleMount`. `RunTests` expands config flags into suites.

## Control Flow

Each test removes the shared cache directory first. `TestCacheMiss` creates a 30 MiB file, reads 2 MiB at offset 10 MiB, and expects exactly one `.bin` chunk file. `TestCacheHit` populates cache from the primary mount, records cache file mod times, stats the file on the secondary mount to warm metadata, reads the same chunk from secondary, compares content, requires the cache count to remain unchanged, and requires cache file mod times to remain unchanged. `TestCacheHitSingleMount` performs the same no-modification check for two reads through one mount.

## State and Persistence Behavior

State spans two mounted directories, GCS test objects, local shared cache files under `gcsfuse-shared-chunk-cache`, and per-mount log files. Cache entries are discovered as `.bin` files, and file modification times are used as a proxy for cache reuse versus re-download.

## Dependencies and Integration Points

It depends on GCSFuse internal cache size constants, static mounting helpers, operations read/create helpers, setup cleanup/log helpers, `filepath.WalkDir`, and `testify/suite/require`. It integrates with dual-mount config from `setup_test.go`.

## Risks and Edge Cases

The cache-hit proof relies on unchanged file modification times, which can be coarse on some filesystems. The helper `mountGcsfuse` accepts `mountPoint` by value, so assignments to `mnt.testDirPath` inside the helper do not update the caller's struct; however `setupTestDir` already set the expected path before mounting. GKE mode requires pre-mounted secondary directory when secondary flags exist. Cache layout changes away from `.bin` files would break counters.

## Test Signals

Passing signal is one cached chunk after a partial read, identical bytes from primary and secondary reads, unchanged cache count, and unchanged cache file mod times on cache hits. Failures indicate shared-cache population, cross-mount reuse, cache keying, or cleanup regressions.
