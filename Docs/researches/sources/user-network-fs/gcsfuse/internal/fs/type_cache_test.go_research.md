<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/gcsfuse/internal/fs/type_cache_test.go -->
# Research: sources/user-network-fs/gcsfuse/internal/fs/type_cache_test.go

Purpose: integration tests for metadata type-cache behavior when object names can be both files and explicit directories, and when cache entries expire by size, TTL, zero size, zero TTL, or infinite TTL.

Important APIs/types/functions: common suite `typeCacheTestCommon`; suites `TypeCacheTestWithMaxSize1MB`, `TypeCacheTestWithZeroSize`, `TypeCacheTestWithZeroTTL`, and `TypeCacheTestWithInfiniteTTL`; helpers `createObjectOnGCS`, `statAndConfirmIsDir`, `statAndExpectNotADirectoryError`, and `testNoInsertionSupported`.

Control flow: setup configures `cfg.MetadataCacheConfig.TypeCacheMaxSizeMb` and `TtlSecs`, mirrors TTL into `ServerConfig.DirTypeCacheTTL` and `InodeAttributeCacheTTL`, then mounts. Tests create file and directory objects with the same basename, call `os.Stat` with or without trailing slash, and observe whether cached type hides the newer remote type.

State and persistence behavior: fake GCS objects are mutable independently of cache. Type-cache state maps name to file/explicit-dir/implicit-dir type and can outlive remote changes until TTL or size eviction. Infinite TTL is mapped to a very large duration. Zero size or zero TTL disables insertion so later stat observes current GCS type.

Dependencies and integration points: depends on `metadata.SizeOfTypeCacheEntry`, fake cache clock `cacheClock`, stat/lookup control flow in `fileSystem.LookUpInode`, and path trailing slash handling.

Risks: stale type-cache entries can cause `not a directory` errors or report a file as a directory after remote changes. Size eviction test creates many long names in parallel, so it is performance-sensitive. Global variables are mutated by suite setup and require serial ogletest behavior.

Test signals: no initial entry gives ENOENT, file hides later dir until eviction, dir hides later file, size-based eviction admits updated dir type, TTL eviction admits updated type, zero size/TTL disable insertion, and infinite TTL never expires even after simulated 100 years.
<!-- END_FILE_RESEARCH: sources/user-network-fs/gcsfuse/internal/fs/type_cache_test.go -->
