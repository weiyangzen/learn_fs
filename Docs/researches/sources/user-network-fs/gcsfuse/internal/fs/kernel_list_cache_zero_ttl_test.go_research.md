# sources/user-network-fs/gcsfuse/internal/fs/kernel_list_cache_zero_ttl_test.go

Purpose: tests kernel list cache behavior when `KernelListCacheTtlSecs` is `0`, meaning directory listings should always be served fresh from gcsfuse rather than retained in the kernel list cache.

Important APIs/types: `KernelListCacheTestWithZeroTtl` embeds the common kernel-list-cache fixture and configures implicit directories, zero kernel-list-cache TTL, zero metadata-cache TTL, rename dir limit, and noop metrics/tracing. The suite uses the same `SkipTestForUnsupportedKernelVersion` guard as other kernel list cache suites.

Control flow and state: `TestKernelListCache_AlwaysCacheMiss` opens and lists `explicitDir`, verifies the initial two files, closes the directory handle, creates `explicitDir/file3.txt` directly in the bucket, and lists again. With zero TTL, the second listing should include all three files, proving gcsfuse handled the read instead of the kernel serving the old cached entries.

Dependencies and integration: depends on shared helpers from `kernel_list_cache_test.go`, the mounted filesystem, fake bucket object creation/deletion, `cfg`, `metrics`, `tracing`, and FUSE/kernel support for list-cache invalidation. Metadata cache TTL is disabled to isolate kernel list cache behavior.

Risks: like the positive and infinite TTL suites, it depends on deterministic entry order and an environment where the list cache feature is supported. It covers explicit directories only; implicit zero-TTL semantics are indirectly covered by the positive-TTL file’s implicit miss test.

Test signals: a failure means zero TTL is allowing stale kernel listings, gcsfuse is not invalidating promptly, or the test environment’s kernel cache semantics differ from expectations.
