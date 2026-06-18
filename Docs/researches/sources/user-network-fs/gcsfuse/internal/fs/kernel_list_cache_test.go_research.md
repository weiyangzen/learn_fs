# sources/user-network-fs/gcsfuse/internal/fs/kernel_list_cache_test.go

Purpose: base and positive-TTL test suite for the kernel list cache feature, where repeated directory listings may be served from the kernel page cache unless TTL expiry or invalidation forces gcsfuse to serve a fresh listing.

Important APIs/types: `KernelListCacheTestCommon` provides setup/teardown, object creation helpers, and `getFilesAndDirStructureObjects`. `KernelListCacheTestWithPositiveTtl` configures `KernelListCacheTtlSecs` to `1000`, disables metadata cache TTL, enables implicit dirs, and installs noop metrics/tracing. The common object structure includes explicit and implicit directories.

Control flow and state: cache-hit tests list a directory, mutate the bucket by adding `file3.txt`, advance the simulated `cacheClock` within TTL, and expect the old two-entry listing. Cache-miss tests perform the same mutation but advance beyond TTL and expect three entries. `TestKernelListCache_CacheHitAfterInvalidation` demonstrates that after a TTL-driven refresh, a later within-TTL read is cached again. Implicit directory variants repeat the semantics for prefix-inferred directories.

Concurrency tests: `Test_Parallel_OpenDirAndLookUpInode`, `Test_Concurrent_ReadDir`, `Test_Parallel_ReadDirAndFileOperations`, and `Test_Parallel_ReadDirAndDirOperations` run goroutines against the same directory, mixing opens/stats/readdirs with create/rename/delete of files and directories. They use five-second timeouts to detect deadlocks or race conditions.

Dependencies and integration: relies on FUSE mount behavior via `os`, fake bucket helpers, shared `cacheClock`, `cfg`, `metrics`, and `tracing`. The tests integrate with kernel-level cache invalidation and gcsfuse directory operation locking.

Risks: listing order is assumed. Timeout-based deadlock tests can be environment-sensitive. The signal for kernel cache behavior is indirect: unchanged listing after bucket mutation means the second read did not reach gcsfuse.

Test signals: protects positive TTL semantics, implicit-dir cache behavior, post-expiry refresh, and concurrent directory operation liveness.
