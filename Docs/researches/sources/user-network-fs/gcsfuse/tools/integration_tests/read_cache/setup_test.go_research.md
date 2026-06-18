# sources/user-network-fs/gcsfuse/tools/integration_tests/read_cache/setup_test.go

## Purpose

`setup_test.go` is the package harness for read-cache integration tests. It centralizes constants, environment state, fallback test configuration, mount selection, log/cache path setup, and cleanup for suites that validate GCSFuse file cache, range read caching, metadata TTL behavior, chunk cache, regex include/exclude rules, remount behavior, and parallel download behavior.

## Important APIs, Types, and Functions

Important constants include cache sizes, file sizes, chunk sizes, offsets, TTLs, cache directory names, and retry timings used by the sibling read-cache tests. The package-level `env` struct stores the `storage.Client`, context, active test directory, `test_suite.TestConfig`, bucket type, and cache directory path. `setupLogFileAndCacheDir` selects a per-suite log and cache directory, with special handling for GKE-mounted-directory mode and legacy GKE paths. `mountGCSFuseAndSetupTestDir` mounts GCSFuse using the current `mountFunc` and creates a unique GCS-backed test directory. `TestMain` is the main orchestrator. `overrideFilePathsInFlagSet` rewrites `/gcsfuse-tmp` placeholders into the actual temp root for non-GKE runs.

## Control Flow

`TestMain` parses setup flags, reads the config file, and if `ReadCache` config is absent synthesizes a large matrix of `ConfigItem` entries. Those entries map run names such as `TestSmallCacheTTLTest`, `TestRangeReadTest`, `TestChunkCacheTest`, and regex/cache variants to explicit GCSFuse flag strings and bucket compatibility maps. It then creates the storage client, handles mounted-directory mode, prepares the test bucket directory, rewrites temp paths, and runs the package three times: static mounting, dynamic mounting, and only-dir mounting. Each phase changes `mountDir` and `mountFunc`, then calls `m.Run`. Cleanup removes both normal and only-dir test prefixes from GCS.

## State and Persistence Behavior

The harness mutates global package state (`testEnv`, `mountDir`, `rootDir`, `mountFunc`) between mounting phases and across suite runs. It creates local cache directories and JSON log files under a GCSFuse temp directory, and it creates/deletes test object prefixes in the target bucket. Cache directories are not automatically cleaned by GCSFuse on mount, so sibling suites explicitly remove them between tests. The fallback config includes duplicate assignment to config index 13 for job chunk parallel-download variants; later assignment overrides the earlier list.

## Dependencies and Integration Points

The file depends on Google Cloud Storage client APIs, GCSFuse internal cache unit constants, integration `client`, `setup`, `test_suite`, and mounting helpers for static, dynamic, and only-dir modes. It integrates with all `read_cache` sibling suites through shared constants and helpers, and with the higher-level mounted-directory runner through `setup.RunTestsForMountedDirectory`.

## Risks and Edge Cases

The harness is sensitive to path rewriting, especially `/gcsfuse-tmp`, GKE-mounted-directory paths, and legacy log paths. Misconfigured run names or compatibility maps can silently skip intended suites. Because `m.Run` is invoked multiple times with mutable global mount state, suites must not assume one-time package state. The generated fallback matrix is large and easy to drift from YAML config. Time-based TTL tests can be flaky under high GCS latency unless their retry wrappers are used.

## Test Signals

Strong signals are successful execution of the read-cache package across static, dynamic, and only-dir mounting with flat, HNS, and zonal compatibility. Logs should be produced in the configured JSON log files, cache directories should be isolated per test name, and cleanup should leave no `ReadCacheTest` or only-dir test prefixes in the bucket.
