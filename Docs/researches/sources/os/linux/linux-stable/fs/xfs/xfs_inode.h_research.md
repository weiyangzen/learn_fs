# File Research: sources/os/linux/linux-stable/fs/xfs/xfs_inode.h

## Purpose

Defines the kernel-only XFS incore inode structure, inode state flags, lock flags/subclasses, inline helpers, and core inode operation prototypes.

## Main Types

- `typedef struct xfs_inode`
  - Embeds the VFS inode.
  - Stores mount, dquots, inode number, imap, data/attr/COW forks, log item, inode locks, pin count, inactivation list node, health bitmaps, flags, block counts, project id, extent hints, metatype, unlinked-list pointers, and pending I/O completion state.
- `enum layout_break_reason`
  - `BREAK_WRITE`
  - `BREAK_UNMAP`

## Main Inline Helpers

- Fork access and sizing:
  - `xfs_inode_has_attr_fork`
  - `xfs_ifork_ptr`
  - `xfs_inode_fork_boff`
  - `xfs_inode_data_fork_size`
  - `xfs_inode_attr_fork_size`
  - `xfs_inode_fork_size`
- VFS/XFS conversions:
  - `XFS_I`
  - `VFS_I`
  - `VFS_IC`
- Size and EOF handling:
  - `XFS_ISIZE`
  - `xfs_new_eof`
- Flag manipulation:
  - `xfs_iflags_set`
  - `xfs_iflags_clear`
  - `xfs_iflags_test`
  - test-and-set/clear variants
- Feature checks:
  - reflink, metadata directory, internal inode, zoned realtime inode, COW inode, bigtime, large extent counts, big realtime allocation, hardware/software atomic write support.

## State Flags

Defines core incore inode flags, including:

- `XFS_IRECLAIM`
- `XFS_ISTALE`
- `XFS_IRECLAIMABLE`
- `XFS_INEW`
- `XFS_IFLUSHING`
- `XFS_IPINNED`
- `XFS_IEOFBLOCKS`
- `XFS_NEED_INACTIVE`
- `XFS_IRECOVERY`
- `XFS_ICOWBLOCKS`
- `XFS_INACTIVATING`
- `XFS_IQUOTAUNCHECKED`
- `XFS_IREMAPPING`

It also defines aggregate reset/reclaim masks.

## Locking API

Defines lock mode bits for:

- IOLOCK shared/exclusive
- ILOCK shared/exclusive
- MMAPLOCK shared/exclusive

Defines lockdep subclass encoding for parent locking, realtime metadata inodes, and inode-number ordered multi-inode locking.

## Main Prototypes

Exports inode operations for:

- namespace mutation: lookup, create, tmpfile, remove, link, rename
- locking: lock/unlock/demote/assert, shared map locks, multi-inode lock helpers
- truncation, freeing, creation, inactivation
- pin waiting, inode flush clustering, log force
- unlinked-list lookup/reload
- layout breaking
- quota allocation for creates
- block counting and allocation unit sizing

## Important Invariants

- `i_flags_lock` protects `i_flags`, `i_checked`, and `i_sick` updates.
- Unlinked-list pointer fields are updated only with AGI locking.
- `XFS_ISIZE` returns VFS size for regular files but disk size for other inode types.
- Internal inode detection changes depending on whether metadata directories are enabled.
- IOLOCK must be acquired before MMAPLOCK, and MMAPLOCK before ILOCK.
- Lock subclass fields are limited by lockdep subclass capacity.

## Research Notes

This header is the primary shared contract for XFS inode state. Its inline helpers encode many policy decisions, especially around internal metadata inodes, realtime/zoned behavior, COW semantics, and multi-lock ordering.
