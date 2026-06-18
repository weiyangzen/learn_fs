# File Research: sources/os/linux/linux/fs/xfs/libxfs/xfs_health.h

## Purpose

`xfs_health.h` defines the in-core metadata health model for XFS. It declares sickness bitmasks, checked/sick semantics, health mutation/query APIs, and helpers for mapping internal health to geometry, bulkstat, and health monitor reports.

## Main Content

- Documents the health model:
  - `checked && sick`: metadata was checked and needs repair.
  - `checked && !sick`: metadata was checked and is healthy.
  - `!checked && sick`: runtime evidence of trouble without a full check.
  - `!checked && !sick`: not examined since mount.
- Defines filesystem-wide sickness bits:
  - Counters, quotas, quota counts, nlinks, metadata directory tree, metadata paths.
- Defines realtime group sickness bits:
  - Superblock, bitmap, summary, rmapbt, refcountbt.
- Defines allocation group sickness bits:
  - SB, AGF, AGFL, AGI, bnobt, cntbt, inobt, finobt, rmapbt, refcountbt, bad inodes.
- Defines inode sickness bits:
  - Core, data/attr/CoW bmap forks, directory, xattrs, symlink, parent pointers, directory tree.
  - Zapped fork/directory/symlink bits.
  - `XFS_SICK_INO_FORGET` to avoid propagating some inactivation state.
- Groups sickness bits into primary, secondary, indirect, and all masks.
- Declares mutation and query APIs:
  - Mark sick/corrupt/healthy for fs, group, AG, realtime group, and inode scopes.
  - Measure sickness for fs, group, and inode.
  - Helpers to mark bmap, btree, dirattr, and da-args sickness.
- Provides health query helpers:
  - `xfs_fs_has_sickness`, `xfs_group_has_sickness`, `xfs_inode_has_sickness`.
  - Healthy checks for fs, AG, rtgroup, and inode.
- Declares export helpers:
  - `xfs_fsop_geom_health`.
  - `xfs_ag_geom_health`.
  - `xfs_rtgroup_geom_health`.
  - `xfs_bulkstat_health`.
- Defines `xfs_metadata_is_sick(error)` for corruption/CRC error classification.
- Declares health monitor mask conversion helpers.

## Key Interfaces and Invariants

- Runtime corruption detection calls `mark_sick`, which does not imply a complete scan.
- Scrub/repair tooling calls `mark_corrupt` or `mark_healthy` to update both sick and checked state.
- AG and realtime group health are stored in `struct xfs_group`.
- User-visible geometry and bulkstat health fields are derived from these internal masks.

## Dependencies

Forward declares core XFS structures and is consumed by scrub, repair, btree, inode, AG, realtime group, ioctl, and monitor code.
