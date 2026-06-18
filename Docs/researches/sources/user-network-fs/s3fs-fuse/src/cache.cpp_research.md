<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/s3fs-fuse/src/cache.cpp -->
# sources/user-network-fs/s3fs-fuse/src/cache.cpp

Purpose: Implements the process-wide `StatCache` for s3fs path metadata, negative entries, directory object lists, and symlink targets.

Important APIs, types, and functions: Implements `GetCacheSize`, `SetCacheSize`, `GetStat`, `GetS3ObjList`, `AddStatHasLock`, two `AddStat` overloads, `AddS3ObjList`, `UpdateStat`, `AddNegativeStat`, `ClearNoTruncateFlag`, `TruncateCacheHasLock`, `DelStatHasLock`, `DelStat`, `GetSymlink`, `AddSymlink`, `RawGetChildStats`, `GetChildStatList`, `GetChildStatMap`, and `Dump`. Static `stat_cache_lock` protects all tree operations. The root cache node is `pMountPointDir`.

Control flow: Reads lock the cache, find nodes by path and optional ETag, handle negative entries as misses while still returning type, and copy stat/meta/list/symlink data out. Writes lock the cache, add or overwrite entries in the `DirStatCache` tree, then truncate expired entries when count exceeds `CacheSize`. Negative cache insertion removes any existing entry first, then stores a `NEGATIVE` node if caching is enabled. Symlink insertion replaces non-symlink entries and stores target text as extra data. Child stat retrieval merges cached child names/types into caller-provided lists/maps.

State and persistence: Entirely in-memory. Default `CacheSize` is 100,000 entries. `NoTruncate` entries protect newly created but not-yet-uploaded files from eviction until cleared. Directory/list and symlink caches share stat cache sizing and timeout behavior through underlying cache nodes.

Dependencies and integration points: Depends on `cache_node.h` tree/node behavior, `s3objlist.h`, `metaheader.h`, object type enums, logging macros, and thread-safety annotation macros from `common.h`. It supports FUSE operations in other modules that need path metadata without repeated S3 HEAD/LIST calls.

Risks: `SetCacheSize` is not locked, so concurrent size changes can race with readers/writers. Several methods return true when caching is disabled, which may be interpreted as success without data by careless callers (`GetSymlink` returns true when size < 1). Truncation only removes expired/truncatable nodes; protected or non-empty directory nodes can let cache count exceed target. Child cache merging is best-effort and returns true even when no directory cache exists.

Test signals: Unit tests should cover positive stat hits, ETag mismatch, negative cache type/miss behavior, size zero behavior, add/update/delete, mount-point clearing, no-truncate clearing, truncation when over capacity, symlink replacement/update, S3 object list caching, child list/map merging, and concurrent access under ThreadSanitizer.
<!-- END_FILE_RESEARCH: sources/user-network-fs/s3fs-fuse/src/cache.cpp -->
