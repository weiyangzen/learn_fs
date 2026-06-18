<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/gcsfuse/tools/integration_tests/kernel_list_cache/infinite_kernel_list_cache_test.go -->
# sources/user-network-fs/gcsfuse/tools/integration_tests/kernel_list_cache/infinite_kernel_list_cache_test.go

## Purpose

This is the broad infinite kernel list cache behavior suite. It validates that infinite TTL preserves stale listings when no local mutation invalidates the cache, and that direct parent directory entries are invalidated by file/directory create, delete, and rename operations made through the mounted filesystem.

## Important APIs, Types, and Functions

`infiniteKernelListCacheTest` owns standard suite setup and teardown. Tests exercise `os.Open`, `Readdirnames`, `os.Create`, `os.Remove`, `os.Mkdir`, `os.Rename`, `operations.CreateDirectory`, `operations.CreateFile`, and direct GCS mutation through `client.CreateObjectInGCSTestDir`.

## Control Flow

`TestKernelListCache_AlwaysCacheHit` seeds a listing, adds a GCS-only object, waits, and expects the cached two-entry listing. File mutation tests seed two entries, add a hidden GCS third entry, then create/delete/rename a mounted file and expect the next listing to refresh. `TestKernelListCache_EvictCacheEntryOfOnlyDirectParent` separately seeds parent and child directory caches, mutates only the child through the mount, injects GCS-only objects in both parent and child, then expects the parent cache to remain stale while the child cache refreshes. Directory add/delete/rename tests follow the same invalidation pattern for subdirectories.

## State and Persistence Behavior

The file is explicitly about kernel list cache state. Direct GCS writes create divergence; mounted filesystem mutations are expected to invalidate exactly the affected parent directory. Random suffixes avoid cross-test name reuse.

## Dependencies and Integration Points

It depends on the package default infinite TTL config, shared setup/client/operations helpers, and kernel support for cache behavior. It is run across configured static, dynamic, only-dir, or mounted-directory modes.

## Risks and Test Signals

The suite assumes stable lexical listing order. It also encodes precise cache invalidation semantics: over-invalidation would fail the direct-parent test, while under-invalidation would fail create/delete/rename tests. Passing signal is stale cache without local mutation and fresh cache for only the direct parent after local mutation.
<!-- END_FILE_RESEARCH: sources/user-network-fs/gcsfuse/tools/integration_tests/kernel_list_cache/infinite_kernel_list_cache_test.go -->
