# File Research: sources/os/linux/linux-stable/fs/fuse/readdir.c

## Purpose
Implements FUSE directory iteration, READDIRPLUS inode linking, and optional directory entry caching for `FOPEN_CACHE_DIR`.

## Key Interfaces
- `fuse_readdir()` is the VFS readdir entry point.
- `fuse_readdir_uncached()` sends `FUSE_READDIR` or `FUSE_READDIRPLUS`.
- `fuse_readdir_cached()` serves entries from the per-inode directory cache.
- `parse_dirfile()` and `parse_dirplusfile()` validate and emit server entries.
- `fuse_direntplus_link()` instantiates or refreshes dentries/inodes from READDIRPLUS responses.

## Control Flow And Behavior
READDIRPLUS is selected when enabled, explicitly advised, automatic at offset zero, or not in auto mode. Uncached reads allocate a buffer, lock the inode around the FUSE request, parse entries, and optionally append them to the directory cache. READDIRPLUS links valid non-dot entries, handles stale dentries, increments lookup counts, updates attributes and entry timeouts, and forces FORGET if linking fails after the server returned a lookup reference.

The cached path validates mtime and i_version at directory offset zero, tracks per-file cache stream position/version, locks cache pages while parsing, and falls back to uncached reads when cache entries are missing or invalidated.

## Dependencies
Uses FUSE read argument filling, FUSE inode/dentry helpers, page cache APIs, inode versioning, ACL cache invalidation, and dir_context emission.

## Risks And Invariants
Dirents must have nonzero valid names, no slash, and record lengths within the reply/cache page. Cache append only succeeds at the current cache end and version. READDIRPLUS must balance lookup references by linking or sending forced FORGET.
