<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/gcsfuse/tools/integration_tests/kernel_list_cache/infinite_kernel_list_cache_delete_dir_test.go -->
# sources/user-network-fs/gcsfuse/tools/integration_tests/kernel_list_cache/infinite_kernel_list_cache_delete_dir_test.go

## Purpose

This suite checks delete-directory behavior when kernel list cache TTL is infinite and metadata caches are disabled for delete-dir consistency. It ensures cached directory listings do not prevent `RemoveAll` from deleting stale or recreated directory contents.

## Important APIs, Types, and Functions

`infiniteKernelListCacheDeleteDirTest` uses the standard mount suite hooks plus `operations.SkipKLCTestForUnsupportedKernelVersion`. Test cases use `operations.CreateDirectory`, `operations.CreateFile`, `os.Open`, `Readdirnames`, `client.CreateObjectInGCSTestDir`, `client.CreateObjectOnGCS`, and `os.RemoveAll`.

## Control Flow

`TestKernelListCache_ListAndDeleteDirectory` lists a two-file directory to seed the kernel cache, injects a third object directly into GCS, and expects `os.RemoveAll` on the directory to succeed. `TestKernelListCache_DeleteAndListDirectory` deletes a directory, recreates it on GCS with a marker and file, lists it to prove the delete invalidated cache state, then calls `RemoveAll` again successfully.

## State and Persistence Behavior

The suite mutates both mounted state and backing GCS state. The default config for this suite disables metadata positive and negative caches to avoid gcsfuse metadata cache masking kernel cache invalidation after deletes.

## Dependencies and Integration Points

It depends on package setup assigning the delete-dir run to flags `--kernel-list-cache-ttl-secs=-1 --metadata-cache-ttl-secs=0 --metadata-cache-negative-ttl-secs=0`. It integrates with GCS explicit directory objects and the kernel list cache invalidation path.

## Risks and Test Signals

The tests are sensitive to directory marker semantics and bucket type behavior. Passing signals are no errors from `RemoveAll`, fresh visibility after delete/recreate, and no stale cache entry preventing a second deletion.
<!-- END_FILE_RESEARCH: sources/user-network-fs/gcsfuse/tools/integration_tests/kernel_list_cache/infinite_kernel_list_cache_delete_dir_test.go -->
