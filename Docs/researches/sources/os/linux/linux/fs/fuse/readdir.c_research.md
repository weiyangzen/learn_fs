# File Research: sources/os/linux/linux/fs/fuse/readdir.c

Implements FUSE directory iteration, readdirplus dentry/inode population, and optional directory entry caching for `FOPEN_CACHE_DIR`.

Key entry points:
- `fuse_readdir()` chooses cached or uncached readdir.
- `fuse_readdir_uncached()` sends `FUSE_READDIR` or `FUSE_READDIRPLUS`.
- `fuse_readdir_cached()` reads from the per-inode readdir cache.
- `parse_dirfile()` and `parse_dirplusfile()` validate and emit server-returned entries.

Important control flow:
- `fuse_use_readdirplus()` honors `do_readdirplus`, `readdirplus_auto`, position zero, and advisory state bits.
- `fuse_add_dirent_to_cache()` appends dirents into page-cache-backed directory cache only if the position matches the cache tail.
- `fuse_readdir_cache_end()` marks cache complete when the server returns EOF.
- Readdirplus entries call `fuse_direntplus_link()` to instantiate or refresh dentries and inodes, update lookup counts, set entry timeouts, and handle stale inode replacement.
- If a readdirplus link fails after a nodeid lookup was gained, `fuse_force_forget()` sends a forced forget.

Dependencies and integration:
- Uses FUSE read request helpers, dcache APIs, page cache APIs, ACL cache invalidation, inode attr versioning, and FUSE lookup/nlookup accounting.

Risks and invariants:
- Dirents with zero names, names larger than `FUSE_NAME_MAX`, slash-containing names, or malformed record lengths cause `-EIO`.
- Cache validity depends on readdir cache version, size, position, directory mtime, and inode i_version.
- Cached iteration resets stream state after seeks or cache version changes.
