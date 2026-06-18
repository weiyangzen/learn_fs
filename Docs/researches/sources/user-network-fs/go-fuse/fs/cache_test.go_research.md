# sources/user-network-fs/go-fuse/fs/cache_test.go

Purpose: validates kernel cache controls exposed through open flags, notifications, symlink caching, and auto invalidation.

Important tests/types: `keepCacheFile` changes content on reads and optionally returns `FOPEN_KEEP_CACHE`; `TestKeepCache` checks cached reads stay stable until `NotifyContent`; `countingSymlink` tracks `Readlink` calls; `TestSymlinkCaching` enables `EnableSymlinkCaching`, verifies one readlink until notification, and documents attr-size truncation behavior; `autoInvalNode` changes mtime/content and `TestAutoInvalData` verifies a stat triggers reread.

State/dependencies: uses mutable in-memory content protected by mutexes and real FUSE kernel caching.

Risks/test signals: strong coverage for cache invalidation semantics, but kernel feature support can skip or vary behavior. Timing uses short TTLs, which may be flaky on slow systems.
