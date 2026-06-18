# sources/user-network-fs/s3fs-fuse/src/fdcache_stat.cpp

Purpose: Implements `CacheFileStat`, the sidecar file manager for persisted `PageList` metadata under the cache stat tree.

Important APIs and functions: Static helpers build and manage paths: `GetCacheFileStatTopDir`, `MakeCacheFileStatPath`, `CheckCacheFileStatTopDir`, `DeleteCacheFileStat`, `DeleteCacheFileStatDirectory`, and `RenameCacheFileStat`. Instance APIs include constructor/destructor, `SetPath`, `OverWriteFile`, `RawOpen`, `Open`, `ReadOnlyOpen`, and `Release`.

Control flow: Sidecar paths are `<cache_dir>/.<bucket>.stat/<object path>`. `OverWriteFile` writes to a temporary `.tmpstat.XXXXXX` in the same directory and renames it over the target. `RawOpen` creates parent directories, opens read-only or read-write, takes an exclusive `flock`, seeks to the start, and stores the fd. `Release` unlocks and closes. Rename uses hard-link-plus-unlink after removing an existing destination sidecar.

State and persistence behavior: Each object stores a `path` and open sidecar `fd`. The sidecar content is produced by `PageList::Serialize`. File locking serializes sidecar readers/writers within local processes using advisory locks.

Dependencies and integration points: Depends on `FdManager` for cache root, `S3fsCred::GetBucket`, and utility functions `mkdirp`, `mydirname`, `delete_files_in_dir`, and permission checks. Used by `FdEntity`, `PageList`, and `FdManager::CheckAllCache`.

Risks: Advisory `flock` only works with cooperating processes. `OverWriteFile` does not fsync the temp file or containing directory before rename, so crash durability is best-effort. `RenameCacheFileStat` with hard links can fail across filesystems, though source and target should be in the same stat tree. Empty cache root or bucket disables stat paths.

Test signals: Cache mode integration tests that delete cache/stat files, reopen cached objects, and run cache checks exercise this path. Unit tests for `PageList` stub `CacheFileStat` rather than using real sidecars, so persistence needs integration coverage.
