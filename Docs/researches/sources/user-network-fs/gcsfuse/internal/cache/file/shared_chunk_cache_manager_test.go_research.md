<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/gcsfuse/internal/cache/file/shared_chunk_cache_manager_test.go -->
# sources/user-network-fs/gcsfuse/internal/cache/file/shared_chunk_cache_manager_test.go

## Purpose
This testify test file validates `SharedChunkCacheManager` path generation, regex filtering, chunk sizing, temp-name generation, and permission accessors.

## Important fixtures and APIs
Tests construct managers with temporary directories and targeted `cfg.FileCacheConfig` values. Fake buckets and minimal objects are used for `ShouldExcludeFromCache`. Table-driven tests cover include/exclude combinations, offsets, chunk sizes, object directory hashes, chunk file paths, and temp path expectations.

## Control flow and state behavior
Constructor tests assert the manager stores cache directory and computes `chunkSize` from `SharedCacheChunkSizeMb`. Regex tests confirm no-filter caching, include-only rejection of non-matches, exclude-only rejection of matches, and exclude precedence when both regexes match. Path tests hard-code expected SHA256 shard paths, acting as compatibility tests for the hash input format. Temp path tests check `<chunk>.16hex.tmp` format and generate 100 paths for one chunk to detect collisions.

## Dependencies and integration points
The suite depends on `t.TempDir`, `filepath`, testify assert/require, `cfg.FileCacheConfig`, fake GCS buckets, and `timeutil.RealClock`. It is tightly coupled to `computeObjectHash` output, which is useful for compatibility but makes intended hash-format changes require test updates.

## Risks and edge cases
The "default chunk size" test expects zero when config is zero, which documents a potentially dangerous default if callers later divide by chunk size. Temp collision testing with 100 random values is probabilistic and cannot prove uniqueness. Regex invalid-input behavior is not tested, despite constructor warning-and-ignore logic.

## Test signals
Signals include stable shared-cache directory layout, deterministic chunk file naming by byte offsets, include/exclude cache policy, random temp suffix format, practical temp uniqueness, and preservation of configured file and directory permissions.
<!-- END_FILE_RESEARCH: sources/user-network-fs/gcsfuse/internal/cache/file/shared_chunk_cache_manager_test.go -->
