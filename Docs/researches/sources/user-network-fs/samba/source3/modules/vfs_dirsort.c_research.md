# sources/user-network-fs/samba/source3/modules/vfs_dirsort.c

## Purpose
`vfs_dirsort.c` returns directory entries in sorted, case-insensitive order by caching the entire directory listing.

## Important APIs, Types, And Functions
`struct dirsort_privates` tracks cached `struct dirent` entries, position, mtime, underlying `DIR *`, and open fsp. `open_and_sort_dir()` reads all entries through the next `readdir`, grows the cache, and sorts with `TYPESAFE_QSORT()` using `strcasecmp_m()`. Hooks implement fdopendir, readdir, rewind, and closedir.

## Control Flow
On fdopendir the lower directory is opened and fully cached/sorted, then private state is linked into handle data. Readdir finds state by `DIR *`, refreshes the cache if directory mtime changed, and returns the next cached entry. Rewind resets the cached position. Closedir unlinks state, delegates close, and frees memory.

## State And Persistence
State is per-open-directory memory. The cache is invalidated only by mtime changes. Nothing persists.

## Dependencies And Integration Points
The module uses Samba directory VFS hooks, talloc, DLIST, `vfs_stat_fsp()`, `SMB_VFS_STAT()`, and locale-aware string comparison.

## Risks
Large directories can consume high memory. Mtime granularity can miss changes. Copying `struct dirent` by value can be platform-sensitive. Cache rebuild failures may disrupt enumeration. The unused `smb_fname` path mode suggests incomplete legacy support.

## Test Signals
Test sorted order, rewind, multiple open directories, mutation during enumeration, large directories, lower open/read failure, and cleanup on closedir.
