# File Research: sources/os/linux/linux-stable/fs/xfs/libxfs/xfs_trans_space.h

## Purpose

Defines block-space reservation macros for XFS metadata operations and declares namespace reservation helper functions.

## Main Macro Groups

- Bmap and extent growth:
  - `XFS_MAX_CONTIG_BMAPS_PER_BLOCK`
  - `XFS_EXTENTADD_SPACE_RES`
  - `XFS_NEXTENTADD_SPACE_RES`
- Data-device rmap:
  - `XFS_MAX_CONTIG_RMAPS_PER_BLOCK`
  - `XFS_RMAPADD_SPACE_RES`
  - `XFS_NRMAPADD_SPACE_RES`
- Realtime rmap:
  - `XFS_MAX_CONTIG_RTRMAPS_PER_BLOCK`
  - `XFS_RTRMAPADD_SPACE_RES`
  - `XFS_NRTRMAPADD_SPACE_RES`
- Directory/attribute operation space:
  - `XFS_DAENTER_*`
  - `XFS_DIRENTER_SPACE_RES`
  - `XFS_DIRREMOVE_SPACE_RES`
- Inode allocation/free:
  - `XFS_IALLOC_SPACE_RES`
  - `XFS_IFREE_SPACE_RES`
- Operation-specific reservations:
  - add attr fork
  - attr remove/set
  - direct I/O strategy
  - growfs
  - growfs realtime
  - quota allocation

## Important Invariants

- Realtime rmap reservations use realtime rmap btree min/max records and maxlevels.
- Historical reflink rmap maxlevel behavior is preserved by `XFS_OLD_REFLINK_RMAP_MAXLEVELS`.
- Directory operations account for both directory btree blocks and bmap btree growth.

## Research Notes

This header provides macro-level block reservation formulas used by higher-level transaction and operation code.
