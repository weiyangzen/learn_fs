<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/gcsfuse/tools/integration_tests/kernel_list_cache/finite_kernel_list_cache_test.go -->
# sources/user-network-fs/gcsfuse/tools/integration_tests/kernel_list_cache/finite_kernel_list_cache_test.go

## Purpose

This suite validates finite kernel list cache TTL behavior. With a 5-second kernel list cache TTL, the first post-mutation listing should remain stale inside the TTL and a later listing should refresh after the TTL expires.

## Important APIs, Types, and Functions

`finiteKernelListCacheTest` mirrors the disabled/infinite suite shape with mount setup and teardown. `TestKernelListCache_CacheHitWithinLimit_CacheMissAfterLimit` uses `operations.SkipKLCTestForUnsupportedKernelVersion`, filesystem directory creation/listing, direct GCS object creation, and `time.Sleep` to bracket the TTL.

## Control Flow

The test creates two files under an explicit directory, lists the directory once, then creates `file3.txt` directly in GCS. After sleeping 2 seconds, it reopens and lists the directory and expects only the original two entries, demonstrating a kernel cache hit. After sleeping 3 more seconds, it lists again and expects all three entries, demonstrating cache expiry and refresh from gcsfuse/GCS.

## State and Persistence Behavior

The important state is kernel-held directory list data and the backing GCS object set. The file uses a single test directory per test and does not modify global configuration beyond the suite's mount flags.

## Dependencies and Integration Points

It depends on kernel support for the list-cache feature, package `setup_test.go` providing `--kernel-list-cache-ttl-secs=5 --rename-dir-limit=10`, and shared client/operations utilities. It participates in the same mounting matrix as the other kernel list cache suites.

## Risks and Test Signals

Timing is the main risk: sleeps assume TTL starts around the first listing and that 2+3 seconds crosses the 5-second boundary reliably. Passing signal is stale listing inside TTL followed by fresh listing after TTL.
<!-- END_FILE_RESEARCH: sources/user-network-fs/gcsfuse/tools/integration_tests/kernel_list_cache/finite_kernel_list_cache_test.go -->
