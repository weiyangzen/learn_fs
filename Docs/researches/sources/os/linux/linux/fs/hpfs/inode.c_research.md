# File Research: sources/os/linux/linux/fs/hpfs/inode.c

Purpose: Implements HPFS inode initialization, read, writeback, setattr, dirty write-on-close support, and eviction cleanup.

Key functions:
- `hpfs_init_inode()` initializes VFS inode defaults from mount options and clears HPFS-private caches/flags.
- `hpfs_read_inode()` maps an fnode, reads UID/GID/MODE/DEV/SYMLINK EAs when enabled, configures special files/symlinks/directories/regular files, and computes size/block/link metadata.
- `hpfs_write_inode_ea()` writes UID/GID/MODE/DEV EAs when mount options allow writable EAs.
- `hpfs_write_inode()` finds the parent inode and delegates writeback unless root/unlinked.
- `hpfs_write_inode_nolock()` updates fnode and matching dirent metadata, including size, timestamps, read-only bit, and EA size.
- `hpfs_setattr()` validates UID/GID range, prevents extension by truncate, applies size changes, copies attributes, and writes inode metadata.
- `hpfs_write_if_changed()` writes dirty inodes.
- `hpfs_evict_inode()` truncates page cache and removes the fnode for unlinked inodes.

Dependencies and integration:
- Uses fnode/dnode mapping, EA helpers, directory-entry lookup by fnode, file truncation, and global HPFS locking.

Risk notes:
- Root inode writeback is skipped.
- Inode metadata is mirrored between fnodes and dirents, requiring successful parent/dirent lookup.
- UID/GID EAs are limited to 16-bit values.
