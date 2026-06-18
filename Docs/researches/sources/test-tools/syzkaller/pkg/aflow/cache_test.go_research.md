# sources/test-tools/syzkaller/pkg/aflow/cache_test.go

## Purpose

`cache_test.go` validates cache persistence, purging, object storage, object retrieval, and cached ID validation.

## Important APIs, Types, and Functions

Tests use `newTestCache`, `Cache.Create`, `Release`, `cacheCreateObject`, `cacheReadObject`, public `CacheObject`, and `RetrieveObject`. `TestCache`, `TestCacheObject`, `TestCacheReadObject`, `TestRetrieveObject`, and `TestRetrieveObject_InvalidID` are the main cases.

## Control Flow

`TestCache` creates entries, verifies hits avoid repopulation, verifies failed population deletes directories, recreates the cache from disk, injects a stray metadata-less directory, and forces max-size purging with a mocked clock. Object tests write/read JSON payloads and verify last-used timestamps. Invalid ID tests cover path traversal, missing slash format, and empty path parts.

## State and Persistence Behavior

The tests use temp directories and mocked time. They intentionally create real files and directories to validate startup scanning, metadata, disk usage, mtime updates, and deletion.

## Dependencies and Integration Points

They use `osutil` for file writes and existence checks, `testify/require`, and `NewTestContext` for public object retrieval.

## Risks and Edge Cases

Disk usage can be filesystem-block dependent, so tests use broad size margins rather than exact byte counts. CI environment differences could affect symlink or disk behavior, but temp-dir isolation keeps blast radius low.

## Test Signals

The tests are strong signals for cache correctness around stale directories, LRU-like purging, reference-count release, JSON object lookup, and safe cached ID parsing.
