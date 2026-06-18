<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/vfs/vfscache/cache_test.go -->
# sources/user-network-fs/rclone/vfs/vfscache/cache_test.go

## Purpose
Tests the `vfscache.Cache` manager's lifecycle, item registry, local path creation, purging, quota enforcement, rename/remove behavior, cleaner loop, modtime setting, stats, and writeback queue plumbing.

## Important APIs, Types, and Functions
Helpers include `itemAsString`, `itemSpaceAsString`, `itemWrite`, path assertions, `addVirtual`, `newTestCacheOpt`, and `newTestCache`. Tests cover `New`, open counts, mkdir behavior, purge old, purge over quota, min free space, purge clean, in-use, dirty item, exists/remove, rename, cleaner, set modtime, total in use, dump, stats, queue, and queue expiry.

## Control Flow
Each test creates a test remote and cache with cleaner/writeback/handle caching mostly disabled for determinism. Tests create/open/truncate/close cache items, manipulate access times and quota options, call purge/clean methods directly, and assert item maps, local filesystem paths, `used` totals, and returned rc parameters.

## State and Persistence Behavior
Tests validate both in-memory `c.item` and actual files under cache data/meta roots. Cleanup removes cache roots and cancels the context. Some tests directly adjust item metadata such as `ATime` to force eviction order.

## Dependencies and Integration Points
Uses local backend import, `fstest`, `diskusage`, `config.GetCacheDir`, `writeback`, `vfscommon.Options`, and item helpers from other vfscache tests. It exercises cache/item/writeback interactions but usually disables background behavior for deterministic direct calls.

## Risks and Edge Cases
Many tests inspect internal fields, making them sensitive to representation changes. Min-free-space behavior is skipped when disk usage is unsupported and depends on actual host free space. Cleaner timing test uses eventual sleeps and may be timing-sensitive.

## Test Signals
Strong signal for cache eviction, quota accounting, local persistence paths, rename/remove integrity, and rc stats/queue plumbing.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/vfs/vfscache/cache_test.go -->
