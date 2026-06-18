<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/cmd/serve/restic/cache_test.go -->
# sources/user-network-fs/rclone/cmd/serve/restic/cache_test.go

Source read: complete file, 55 lines, 1077 bytes, sha256 `89b7efb7cda3956c9611749abf28bdfdbc13310e589c0cb8bf4b0554efdcdd4e`. Final split target: `Docs/researches/sources/user-network-fs/rclone/cmd/serve/restic/cache_test.go_research.md`.

## Purpose
Tests the restic object cache implementation.

## Important APIs, types, and functions
Adds a test-only `String` method to expose sorted cache keys. `TestCacheCRUD` covers add/find/remove. `TestCacheRemovePrefix` checks child removal and full clear.

## Control flow
Tests create mock objects, mutate a cache, and compare deterministic comma-joined key listings.

## State and persistence behavior
State is test-local in-memory cache entries guarded by the cache mutex.

## Dependencies and integration points
Depends on `mockobject`, sorting, strings, and testify assertions.

## Risks and edge cases
Only enabled-cache behavior is tested; disabled-cache no-op behavior is not directly asserted here.

## Test signals
Provides direct signal that exact keys are preserved while descendants are removed and `/` clears all.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/cmd/serve/restic/cache_test.go -->
