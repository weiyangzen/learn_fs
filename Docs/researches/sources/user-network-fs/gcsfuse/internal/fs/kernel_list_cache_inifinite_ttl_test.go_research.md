# sources/user-network-fs/gcsfuse/internal/fs/kernel_list_cache_inifinite_ttl_test.go

Purpose: tests kernel directory-list caching when `KernelListCacheTtlSecs` is `-1`, meaning the kernel list cache should not expire by time. The filename contains the spelling `inifinite`, but the suite name and config describe infinite TTL behavior.

Important APIs/types: `SkipTestForUnsupportedKernelVersion` skips suites when `common.IsKLCacheEvictionUnSupported` reports an unsupported kernel. `KernelListCacheTestWithInfiniteTtl` embeds `fsTest` and `KernelListCacheTestCommon`. `SetupSuite` enables implicit directories, sets kernel list cache TTL to `-1`, disables metadata cache TTL, sets rename dir limit, and uses noop metrics/tracing.

Control flow and state: the tests inherit common setup that creates `explicitDir/`, two explicit files, and implicit directory files, then sets `cacheClock`. `TestKernelListCache_AlwaysCacheHit` lists `explicitDir`, creates `file3.txt` out-of-band in the bucket, advances the cache clock by five years, and expects the second listing to still return only the first two files. `TestKernelListCache_RemoveDirAfterListIsCachedWorks` verifies `os.RemoveAll` can delete a cached directory and future reads fail. `TestKernelListCache_RemoveDirAfterListCacheInvalidatesCache` removes a cached directory, recreates content under the same prefix, and expects a fresh listing with only the new file.

Dependencies and integration: uses the mounted filesystem (`os.Open`, `Readdirnames`, `os.RemoveAll`, `os.ReadDir`) plus fake bucket mutation through shared helpers. It is coupled to kernel invalidation behavior and the FUSE notifier/list-cache implementation.

Risks: cache assertions depend on directory entry ordering and on clock-controlled invalidation. The test must be skipped on unsupported kernels, so CI coverage can vary by environment.

Test signals: confirms infinite TTL preserves stale listings until explicit filesystem mutations invalidate the cache.
