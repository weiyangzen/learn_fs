# sources/user-network-fs/rclone/cmd/serve/nfs/cache_test.go

## Purpose

This file tests NFS handle cache backends and the subpath path-rewriter behavior.

## Important APIs, Types, and Functions

Helpers are `testCacheCRUD`, `testCacheThrashDifferent`, and `testCacheThrashSame`. Tests are `TestCache` and `TestPathRewriterHandleStability`.

## Control Flow

For each cache type, tests create a handler with memory-object VFS and temp cache dir, skip symlink cache when unsupported or permission-limited, then verify missing handles, handle creation/readback, invalidation, repeated invalidation, stale-handle behavior, parallel operations, and metadata suffix behavior. Path-rewriter tests compare handles minted from root and subpath FS views.

## State and Persistence Behavior

Disk/symlink tests write into temp cache directories. The test quiets log level temporarily to avoid expected stale-handle noise.

## Dependencies and Integration Points

It depends on object memory Fs, VFS metadata extension, cache selection, and optional Linux `CAP_DAC_READ_SEARCH` for symlink cache.

## Risks and Test Signals

The tests are strong for cache correctness and recent subpath stability. Memory cache is explicitly not concurrency-tested because the upstream caching handler is not thread-safe. Real NFS client behavior is tested elsewhere.
