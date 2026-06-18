# File Research: sources/os/linux/linux-stable/fs/jfs/inode.c

Handles inode instantiation, commit/writeback, eviction, block mapping, page-cache operations, direct I/O, and truncate.

Key functions:
- `jfs_iget()` loads an inode with `diRead()` and assigns operation tables based on file type, including fast symlink handling and special inode setup.
- `jfs_commit_inode()` and `jfs_write_inode()` coordinate transaction commits for dirty inodes and journal flushing.
- `jfs_evict_inode()` truncates pages, frees zero-link filesystem inodes, drops quota state, and releases active AG accounting.
- `jfs_get_block()` maps logical blocks through `xtLookup()`, records not-yet-recorded extents on write, or allocates via `extHint()`/`extAlloc()`.
- `jfs_aops` wires mpage read/write, block write begin/end, bmap, direct I/O, and buffer folio migration.
- `jfs_truncate()` and `jfs_truncate_nolock()` truncate extents transactionally, looping because `xtTruncate()` may not complete atomically.

Integration:
- Central bridge between VFS address-space operations, JFS extent tree (`xtree`), transaction manager, quota, and disk allocation map.

Risk notes:
- Fast symlink null termination guards against corrupt inline data.
- Direct-I/O write failures above `i_size` trigger cleanup via `jfs_write_failed()`.
