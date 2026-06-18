# File Research: sources/os/linux/linux/fs/hfs/inode.c

Purpose: Implements classic HFS inode lifecycle, address-space operations, file operations, fork read/write state, resource fork lookup, setattr, fsync, and file attribute reporting.

Key functions:
- `hfs_read_folio()`, `hfs_write_begin()`, `hfs_bmap()`, `hfs_direct_IO()`, and `hfs_writepages()` connect VFS/page-cache I/O to `hfs_get_block()`.
- `hfs_release_folio()` evicts cached B-tree nodes when their pages are released and no node refs remain.
- `hfs_new_inode()` initializes a newly allocated file or directory inode and updates filesystem counts.
- `hfs_delete_inode()` decrements counts and truncates deleted regular files.
- `hfs_inode_read_fork()` and `hfs_inode_write_fork()` translate catalog/MDB fork extents and sizes to in-memory fields.
- `hfs_iget()` uses `iget5_locked()` with catalog record identity checks.
- `hfs_write_inode()` writes updated catalog records, B-tree headers, and fork extents.
- `hfs_file_lookup()` exposes the resource fork through a synthetic `rsrc` child.
- `hfs_inode_setattr()` enforces HFS permission/ownership limitations and handles truncation.
- `hfs_file_fsync()` flushes inode, delayed MDB work, and block device.
- `hfs_fileattr_get()` reports casefold behavior.

Dependencies and integration:
- Uses catalog, extent, MDB, and B-tree helpers throughout.
- Exports `hfs_aops` and `hfs_btree_aops` for regular files and special B-tree files.
- File and inode operation tables are local, while directory operation tables come from `dir.c`.

Risk notes:
- Resource fork inodes are synthetic and share catalog backing with the main inode; lifecycle coupling via `rsrc_inode` must stay balanced.
- `hfs_file_release()` truncates on final close, so allocation cleanup can be deferred.
- Setattr accepts only limited mode changes and fixed mount uid/gid semantics.
