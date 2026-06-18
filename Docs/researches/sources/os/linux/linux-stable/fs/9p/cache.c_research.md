# File Research: sources/os/linux/linux-stable/fs/9p/cache.c
- Purpose: Implements FS-Cache cookie acquisition for 9P sessions and inodes.
- Main functions: `v9fs_cache_session_get_cookie` and `v9fs_cache_inode_get_cookie`.
- Session flow: Builds a volume name from device/cache tag/aname data and calls `fscache_acquire_volume`, storing the result in `v9ses->fscache`.
- Inode flow: Uses the 9P qid version/path as coherency keys and calls `fscache_acquire_cookie` for regular-file cache state.
- Integration: Used by mount/session setup and inode instantiation/open paths when `CACHE_FSCACHE` is active.
- Risks: Cache identity depends on qid metadata and selected mount cache tag; incorrect tag sharing could affect coherency assumptions.
