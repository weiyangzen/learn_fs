<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/s3fs-fuse/src/cache.h -->
# sources/user-network-fs/s3fs-fuse/src/cache.h

Purpose: Declares the `StatCache` singleton interface and synchronization contract for s3fs metadata, negative, directory-list, and symlink caching.

Important APIs and types: `StatCache::getStatCacheData` returns a function-local singleton. Public methods expose cache sizing, stat reads/writes, S3 object list caching, negative cache insertion, metadata update, no-truncate flag clearing, deletion, symlink cache access, child stat list/map retrieval, and debug dump. Private helpers are annotated with `REQUIRES(StatCache::stat_cache_lock)` and fields with `GUARDED_BY`.

Control flow and integration: Other s3fs modules call this singleton during FUSE lookup/getattr/readdir/readlink/create/update paths. The underlying cache tree starts at mount point `/` and is represented by `DirStatCache`.

State and persistence: Declares static mutex protection, root directory cache node, and maximum cache size. All cached data is process-local and non-persistent.

Dependencies: Includes mutex/string/stat headers plus project headers `common.h`, `metaheader.h`, `s3objlist.h`, and `cache_node.h`.

Risks: Public API returns booleans with nuanced meanings, especially negative cache and disabled-cache cases. Thread-safety annotations help static checking, but only if the toolchain honors them. Singleton lifecycle can make tests order-dependent unless they clear state between cases.

Test signals: Compile with thread-safety annotations, run source unit tests (`test_page_list` adjacent cache structures where applicable), and add direct StatCache tests for all public overloads and concurrency-sensitive paths.
<!-- END_FILE_RESEARCH: sources/user-network-fs/s3fs-fuse/src/cache.h -->
