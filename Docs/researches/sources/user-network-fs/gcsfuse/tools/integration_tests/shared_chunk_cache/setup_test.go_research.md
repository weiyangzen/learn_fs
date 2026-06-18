# sources/user-network-fs/gcsfuse/tools/integration_tests/shared_chunk_cache/setup_test.go

## Purpose

This harness prepares tests for the experimental shared chunk cache. It configures primary and secondary mount directories so two mounts can share the same chunk-cache directory.

## Important APIs, Types, and Functions

Constants define `testDirName` and `GKETempDir`. `env` stores storage client, context, config, and bucket type. `TestMain` loads config, synthesizes a default shared-cache dual-mount config if absent, initializes storage, handles GKE mounted-directory mode, creates a secondary mount directory for GCE mode, runs tests, and cleans the GCS test prefix.

## Control Flow

`TestMain` parses flags, configures `SharedChunkCache` with primary and secondary flags that both enable shared chunk cache and point at `/gcsfuse-tmp/shared-cache`, creates the storage client, handles mounted-directory mode by assigning primary/secondary mounted directories, otherwise prepares a test bucket directory, rewrites temp paths, creates a secondary local mount directory under the test temp root, runs `m.Run`, cleans GCS, and exits.

## State and Persistence Behavior

The harness creates local mount directories and a shared cache directory path, plus bucket objects under `SharedChunkCacheTest`. It stores mutable global `testEnv`. The actual mounting/unmounting is done by the suite in `shared_chunk_cache_test.go`.

## Dependencies and Integration Points

It depends on Cloud Storage, integration `client`, setup/test-suite helpers, and the shared chunk cache suite. It relies on `ConfigItem.SecondaryFlags` and `GCSFuseMountedDirectorySecondary`, which are specific to dual-mount scenarios.

## Risks and Edge Cases

GKE mode assumes both primary and secondary mounted directories are already available. Non-GKE mode creates a secondary mount dir but does not remove it explicitly here. Path rewriting must update both primary and secondary cache-dir flags. The feature is experimental, so flag names and cache layout may change.

## Test Signals

Harness success means dual-mount suite execution receives two mount directories and common cache flags. Failures typically indicate missing secondary mount config, storage setup, or path rewriting issues.
