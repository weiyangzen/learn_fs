# File Research: sources/os/linux/linux/fs/xfs/libxfs/xfs_trans_space.h

## Purpose

`xfs_trans_space.h` defines block-space reservation macros for XFS metadata operations and declares namespace block reservation helper functions.

## Main Content

- Defines worst-case contiguous record capacity for bmap, realtime rmap, rmap, and allocation btrees.
- Defines space needed to add rmap, realtime rmap, and bmap extents.
- Preserves old reflink rmap maxlevels constant for compatibility in reservation calculations.
- Defines directory/attribute entry insertion and removal reservation components.
- Defines inode allocation and inode free reservation components.
- Defines transaction-level space macros for:
  - Add attr fork.
  - Attribute remove/set.
  - Direct I/O strategy.
  - Growfs data and realtime.
  - Quota allocation and quota inode creation.
- Declares block reservation functions for parent pointers and namespace operations.

## Key Interfaces and Invariants

- Reservation macros depend heavily on mount precomputed btree min/max record counts.
- DA reservation macros account for directory blocks fragmenting below directory block size.
- `XFS_IALLOC_SPACE_RES` accounts for finobt when enabled.
- Realtime rmap reservation macros use realtime rmap btree height and record density.

## Dependencies

Depends on mount btree geometry, inode geometry, directory geometry, fork identifiers, and feature predicates such as finobt.
