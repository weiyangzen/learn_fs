# File Research: sources/os/linux/linux/fs/erofs/inode.c

Implements EROFS inode loading, VFS operation assignment, inode lookup, stat attributes, and ioctls.

Key behavior:
- Reads compact or extended on-disk inodes from normal metadata or metabox metadata.
- Validates inode format, datalayout, nonnegative size, chunk format, and compressed-filesystem availability.
- Fills mode, uid/gid, nlink, mtime, size, start block, rdev, xattr size, chunk fields, DAX flag, and dot-omitted state.
- Caches small inline symlink targets as fast symlinks and validates their length/NUL behavior.
- Assigns file, directory, symlink, or special inode operations and address-space operations.
- Uses inode sharing when enabled, switching regular file fops to `erofs_ishare_fops`.
- `erofs_iget()` uses `iget5_locked()` keyed by nid with inode-number squashing on narrow `ino_t`.
- `getattr` reports immutable and compressed attributes and direct-I/O alignment when supported.
- Implements `FS_IOC_GETFSLABEL`.
- Exposes generic, page symlink, and fast symlink inode operation tables.

Important interactions:
- Uses xattr/ACL helpers to cache no-ACL state and list xattrs.
- Calls `erofs_get_aops()` to select compressed, fscache, file-backed, or standard aops.
- DAX is limited to regular flat plain or chunk-based inodes under `DAX_ALWAYS`.
