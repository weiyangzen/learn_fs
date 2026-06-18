# File Research: sources/local-fs/xfsprogs/libxfs/xfs_inode_util.c

## Role

This file provides inode utility operations: converting inode flags to/from user-visible xflags, inheriting creation attributes, initializing new inodes, maintaining the AGI unlinked inode list, updating link counts, and uninitializing freed inodes.

## Flag Conversion

- `xfs_flags2diflags` converts `FS_XFLAG_*` into `XFS_DIFLAG_*`, preserving prealloc and applying directory-only or regular-file-only flags appropriately.
- `xfs_flags2diflags2` converts DAX and CoW extent-size xflags while preserving reflink, bigtime, and large extent counter bits.
- `xfs_ip2xflags` converts incore flags back to user xflags and reports `FS_XFLAG_HASATTR` if the attr fork exists.
- `xfs_get_initial_prid` inherits project id when `PROJINHERIT` is set, otherwise uses root project id.

## Inode Creation

`xfs_inode_init` initializes a newly allocated inode from `xfs_icreate_args`. It sets link count, rdev, uid/gid/project ownership, mode, timestamps, version counter, data fork format, inherited flags, optional attr fork, and transaction logging.

Creation logic handles:

- tmpfiles with zero links
- directories with link count 2
- group inheritance with `XFS_MOUNT_GRPID`
- detached/tree-root creation with root ids
- parent-inherited realtime, extsize, project, noatime, nodump, sync, nosymlinks, nodefrag, filestream, DAX, metadata, and CoW extent size flags
- parent pointer filesystems forcing an attr fork unless the inode is explicitly unlinkable
- adding the attr feature bit to the superblock when initializing an attr fork on a filesystem without the attr bit

Inherited extsize and CoW extsize hints are validated after propagation, and invalid hints are cleared instead of propagating broken realtime-alignment state.

## Unlinked List Maintenance

XFS maintains on-disk per-AG unlinked inode hash chains in the AGI. This file adds an incore doubly linked helper model using `i_prev_unlinked` plus cached inode lookup so removal does not have to linearly scan the singly linked on-disk list.

Key functions:

- `xfs_iunlink` inserts a zero-link inode into the AGI unlinked list.
- `xfs_iunlink_insert_inode` validates the bucket head, updates backrefs, logs the inode next pointer, and updates the AGI bucket.
- `xfs_iunlink_remove` removes an inode from the AGI unlinked list.
- `xfs_iunlink_remove_inode` clears the inode's on-disk next pointer, updates the next inode's backref, updates the previous inode or bucket head, and resets incore pointers.
- `xfs_iunlink_update_bucket` logs a changed AGI bucket.
- `xfs_iunlink_update_backref` updates the next cached inode's prev pointer or reports `-ENOLINK` so reload logic can recover it.

The AGI buffer lock serializes list manipulation and enforces lock ordering.

## Link Count Helpers

`xfs_droplink` decrements link count, logs ctime/core changes, pins the count if it would underflow, and moves the inode to the unlinked list when the count reaches zero.

`xfs_bumplink` increments link count, logs changes, and pins the count if it would exceed the XFS maximum.

## Inode Uninitialization

`xfs_inode_uninit` frees an inode from the on-disk inode index, removes it from the unlinked list, frees local-format data still attached to the data fork, clears mode and flags, resets fork format and attr fork state, applies new default v3 flags2, increments generation, and logs the inode core.

The order frees the inode before removing it from the unlinked list to preserve AGI lock ordering consistent with tmpfile creation.

## Dependencies

This file depends on transaction logging, inode allocation/freeing, AGI reads, health marking, bmap/fork structures, mount feature bits, iunlink reload/log helpers, and VFS-style inode ownership helpers supplied by the userspace platform layer.

## Research Notes

The unlinked list code has tight invariants around AGI bucket validity and incore next/prev coherence. Parent pointer support changes creation behavior by requiring early attr fork creation for linkable files, which affects inode fork layout and transaction reservations.
