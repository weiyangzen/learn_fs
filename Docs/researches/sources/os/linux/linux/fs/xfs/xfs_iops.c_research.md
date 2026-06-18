# File Research: sources/os/linux/linux/fs/xfs/xfs_iops.c

## Role
Implements the Linux VFS inode operations for XFS. It handles inode creation, lookup, linking, unlinking, symlinks, renames, tmpfile creation, getattr/statx, setattr/truncate, timestamp updates, fiemap, security xattrs, DAX flag setup, and inode operation table initialization.

## Main Structures and Entry Points
- `xfs_generic_create` underpins create, mknod, mkdir, and tmpfile.
- `xfs_vn_lookup` and `xfs_vn_ci_lookup` implement normal and ASCII case-insensitive lookup.
- `xfs_vn_link`, `xfs_vn_unlink`, `xfs_vn_symlink`, and `xfs_vn_rename` map VFS namespace operations to XFS directory operations.
- `xfs_vn_getattr` fills `kstat`, including DIO alignment and atomic write statx fields.
- `xfs_vn_setattr`, `xfs_vn_setattr_size`, and `xfs_setattr_nonsize` implement size and non-size attribute changes.
- `xfs_vn_update_time` and `xfs_vn_sync_lazytime` log timestamp changes.
- `xfs_vn_fiemap` delegates data or attr fork extent reporting to iomap.
- `xfs_setup_inode`, `xfs_setup_iops`, and `xfs_diflags_to_iflags` initialize VFS inode state and operation tables.
- `xfs_get_atomic_write_min/max/max_opt` compute advertised atomic write limits.

## Behavior
Creation validates device numbers, prepares POSIX ACLs, pre-creates attr forks when ACL/security xattrs are likely, creates named or temporary inodes, initializes security xattrs and ACLs, installs inode operations, and cleans up created directory entries on post-create failure. Tmpfiles adjust link count to satisfy VFS `d_tmpfile` requirements while preserving XFS unlinked-list rules.

Lookup converts dentries to XFS names and uses `d_splice_alias`; case-insensitive lookup can return `d_add_ci` with the canonical name. Link/unlink/rename convert VFS names to XFS typed names and call XFS namespace helpers, invalidating negative dentries for case-insensitive unlink.

Getattr reports XFS disk size, block counts including delayed blocks, birth time for v3 inodes, immutable/append/nodump flags, block size hints, DIO alignment, COW write alignment, and atomic write limits. Setattr splits size changes from other changes: truncation locks out mmap faults/layouts, waits for direct I/O, zeroes exposed partial blocks, updates page cache size, writes needed ranges to avoid stale exposure, logs disk size before freeing extents, and marks truncated inodes for earlier flush. Non-size updates handle quota allocation/chown, VFS attribute copy, transaction logging, and ACL chmod follow-up.

## Interactions
This file sits between the VFS and XFS core subsystems: directory operations, inode allocation, symlinks, ACLs, xattrs, quota, iomap, file operations, DAX, stable writes, pagecache, block layout breaking, and transaction logging. It exports setup functions used when inodes are read or created.

## Invariants and Error Handling
- Directory inode locks use distinct lockdep classes from non-directories, with metadata directories separated.
- Internal metadata inodes are marked `S_PRIVATE` and stripped of normal xattr behavior.
- Page cache allocations are forced into no-FS reclaim context to avoid recursion.
- Size changes require regular files and exclusive IO/MMAP locks.
- Disk size is logged before block freeing on truncate down to avoid exposing freed/reallocated block contents after crash.
- Lazytime may only mark `I_DIRTY_TIME`; non-lazy nowait timestamp updates return `-EAGAIN`.
