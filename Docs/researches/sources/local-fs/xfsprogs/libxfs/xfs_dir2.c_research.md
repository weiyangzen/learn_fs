# File Research: sources/local-fs/xfsprogs/libxfs/xfs_dir2.c

## Purpose

`xfs_dir2.c` provides the high-level XFS directory API and format dispatcher for libxfs. It initializes directory/attribute geometry, validates inode numbers and names, routes operations to shortform/block/leaf/node implementations, and implements child link, unlink, rename, and exchange workflows including parent pointer updates.

## Main Behavior

Mount setup builds directory and attribute `xfs_da_geometry` from the superblock. Directory geometry includes block/leaf/free/data header sizes, section boundaries, node fanout, max extents, and first data-entry offset. Attribute geometry uses filesystem block size and shares node header sizing.

The basic directory API allocates and populates `xfs_da_args` for create, lookup, remove, replace, and can-enter checks. `xfs_dir2_format` classifies a directory as shortform, block, leaf, or node from inode fork format, file size, and bmap EOF, then the `*_args` dispatchers call the appropriate backend. Lookup supports ASCII case-insensitive filesystems by returning the actual matched name when requested.

Utility functions grow and shrink directory data/free blocks, update `i_disk_size`, validate names against length, slash, and NUL constraints, and switch hashing/comparison between normal and ASCII-CI behavior. Optional live hooks notify online fsck-like consumers of directory entry updates.

Higher-level child operations combine directory entry updates with inode link counts, timestamps, parent pointer xattrs, unlinked-list cleanup for tmpfile/whiteout cases, and `..` updates for directories. `xfs_dir_create_child`, `xfs_dir_add_child`, and `xfs_dir_remove_child` implement link/unlink semantics. `xfs_dir_exchange_children` swaps two existing entries and adjusts directory parents/link counts. `xfs_dir_rename_children` handles target replacement or creation, cross-directory moves, whiteouts, parent pointer changes, and update hooks.

## Dependencies and Risks

This file depends on all directory format backends, bmap growth/shrink, transactions, inode locking/link counts, parent pointers, allocation groups, unlinked-list handling, and optional live hooks. Risks include dispatching based on corrupt directory size/EOF, case-insensitive duplicate handling, link count updates for cross-directory renames, `..` replacement ordering, no-reservation ENOSPC behavior, whiteout/tmpfile state transitions, and keeping parent pointer attr updates atomic with dirent changes.
