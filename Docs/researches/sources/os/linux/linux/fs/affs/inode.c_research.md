# File Research: sources/os/linux/linux/fs/affs/inode.c

Purpose: handles AFFS inode load/store, setattr, eviction, new inode allocation, and directory entry creation.

Key interfaces:
- `affs_iget()`: reads AFFS header block into a VFS inode.
- `affs_write_inode()`: writes mode/protection, size, uid/gid, and timestamps back to disk.
- `affs_setattr()`: validates and applies VFS attribute changes.
- `affs_evict_inode()`: final cleanup, truncate/free on unlink, metadata sync/invalidate.
- `affs_new_inode()` and `affs_add_entry()`: allocate a header block and insert it into a directory hash chain.

Implementation notes:
- `affs_iget()` validates block checksum and `T_SHORT` type, initializes AFFS private fields, converts protection bits to Unix mode, and selects operations by `stype`.
- Directories get `affs_dir_inode_operations` and `affs_dir_operations`; regular files get AFFS file ops and normal/OFS address ops; symlinks use symlink aops.
- UID/GID handling supports mount overrides and MUFS `0xffff` translation.
- Timestamps are converted from AFFS datestamps plus `AFFS_EPOCH_DELTA` and timezone offset.
- `affs_write_inode()` skips unlinked inodes, updates root or normal tail timestamps, writes protection/size/owner fields, fixes checksums, and marks metadata buffers dirty.
- `affs_add_entry()` creates normal entries or additional link header blocks for `ST_LINKFILE`/`ST_LINKDIR`, maintains link chains, and inserts into the parent directory hash table.

Dependencies:
- Depends on AFFS block allocation, checksum, bitmap, hash insertion, dentry name copying, and metadata buffer tracking.

Edge cases:
- Unsupported `ST_LINKFILE` during inode load is treated as bad inode.
- Attribute changes that conflict with mount-enforced uid/gid/mode/protect options return `-EPERM` unless quiet mode is set.
- On add-entry failure, allocated link blocks are freed and locks released.
