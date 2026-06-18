# File Research: sources/os/bsd/freebsd-src/sys/fs/ext2fs/ext2_vnops.c

## Purpose
Defines FreeBSD vnode operations for ext2fs regular files, directories, symlinks, FIFOs, extended attributes, and metadata updates.

## Main Elements
- Registers `ext2_vnodeops` and `ext2_fifoops`.
- `ext2_itimes()` updates access/change/modify timestamps and marks inodes modified.
- Implements create/open/close/access/getattr/setattr/chmod/chown/fsync/mknod/remove/link.
- `ext2_rename()` performs UFS-style multi-step atomic rename best effort, including cross-device checks, link-count protection, sticky/immutable checks, target replacement, `..` rewrite, htree/checksum updates, and source cleanup.
- Optional POSIX.1e ACL inheritance helpers initialize access/default ACLs for new files and directories.
- `ext2_mkdir()` allocates a directory inode, writes `.` and `..`, handles metadata checksum tails, bumps parent link count, and installs the parent entry.
- `ext2_rmdir()` verifies emptiness, removes parent entry, decrements parent links, truncates the removed directory, and purges cache.
- `ext2_symlink()` stores short symlinks inline in inode block pointers or writes long symlink data.
- `ext2_read()` and `ext2_write()` implement buffered I/O with cluster read/write, allocation via `ext2_balloc()`, append handling, max-file-size checks, SUID/SGID clearing, and `IO_UNIT` rollback.
- `ext2_strategy()` maps logical blocks through extents or classic indirect mapping before issuing device I/O.
- Extended attribute VOPs dispatch to inode-resident and external-block extattr storage.
- `ext2_vinit()` sets vnode type, FIFO ops, root flag, and file revision.
- `ext2_makeinode()` allocates and initializes new non-directory inodes before directory insertion.
- `ext2_pathconf()` reports ext2 limits and feature-sensitive link limits.

## Dependencies And Integration
Uses allocation, bmap, truncate, extattr, ACL, htree, checksum, vnode pager, buffer cache, and FreeBSD privilege/access APIs.

## Risk Notes
Rename and directory creation are crash-repairable rather than journal-atomic. Extent-aware paths exist, but behavior depends on the rest of ext2fs extent support. Directory checksums must be updated when directory contents or `..` are rewritten.
