# File Research: sources/os/linux/linux-stable/fs/jfs/jfs_inode.h

This header declares the JFS inode, file operation, export, ioctl, attribute, writeback, and block-mapping interfaces shared across the filesystem.

Key responsibilities:
- Declares `ialloc()` and `jfs_set_inode_flags()`.
- Declares file synchronization, ioctl, file attribute get/set, inode lookup, inode commit/writeback/eviction/dirty/truncation, zero-link cleanup, exportfs parent/fh lookup, block mapping, and setattr entry points.
- Exposes address-space operations, inode operations, file operations, symlink operations, and case-insensitive dentry operations.

Important interactions:
- Included by inode allocation, extent, imap, file, ioctl, export, and directory operation code.
- Provides the cross-file prototypes that connect JFS VFS operations to lower metadata code.

Notable invariants and risks:
- Many declarations here are VFS callbacks; prototype drift would break filesystem registration or operation-table initialization elsewhere.
- `jfs_get_block()` is the block-mapping bridge that ultimately depends on extent allocation/update behavior.

Research notes:
- This is the public internal header for JFS inode-facing code. The implementation is spread across multiple files outside this group.
