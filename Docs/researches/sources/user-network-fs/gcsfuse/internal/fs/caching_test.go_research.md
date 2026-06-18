<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/gcsfuse/internal/fs/caching_test.go -->
# Research: sources/user-network-fs/gcsfuse/internal/fs/caching_test.go

Purpose: integration-tests filesystem consistency behavior when stat caching and directory type caching are enabled, for both single-bucket and multi-bucket mounts, including implicit directories and conflicting names.

Important APIs/types/functions: constants `ttl` and `negativeCacheTTL`; `newLruCache`; `cachingTestCommon.SetUpTestSuite`; suites `CachingTest`, `CachingWithImplicitDirsTest`, and `MultiBucketMountCachingTest`; helper `getMultiMountBucketDir`; tests covering remote creation, remote changes, remote removals, conflict names, local modifier cache updates, implicit directories, symlink type caching, and negative-cache behavior after local removal plus remote recreation.

Control flow: setup wraps fake buckets with `caching.NewFastStatBucket`, using an LRU stat cache and the shared simulated `cacheClock`, then enables `DirTypeCacheTTL`. Tests mutate the uncached fake bucket to simulate remote changes, observe stale results before TTL expiry, advance `cacheClock`, and verify fresh results after expiry. Multi-bucket tests use a shared LRU with per-bucket views to verify isolation.

State and persistence: state includes fake bucket contents, stat-cache entries, directory type-cache entries, and mounted filesystem state. Cache staleness is time-controlled by simulated clock rather than sleeps.

Dependencies and integration points: depends on `internal/storage/caching`, `metadata.NewStatCacheBucketView`, `lru`, fake buckets, `inode.ConflictingFileNameSuffix`, `fusetesting`, metrics/tracing noops, and `fsTest`. It exercises the integration between storage caching and filesystem inode/type lookup.

Risks: these tests intentionally document consistency tradeoffs: remote type changes, deletions, and recreations can remain stale until TTL expiry. Multi-bucket teardown deletes objects through wrapped buckets and assumes cache state is sufficiently isolated/reset by suite lifecycle. Real FUSE mount requirements apply.

Test signals: strong external-behavior signal for cache TTL semantics, same-name file/directory conflicts, symlink versus directory conflicts, implicit directory discovery, bucket-isolated cache keys, and negative entries after local delete.
<!-- END_FILE_RESEARCH: sources/user-network-fs/gcsfuse/internal/fs/caching_test.go -->
