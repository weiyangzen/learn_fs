# File Research: sources/os/linux/linux-stable/fs/xfs/libxfs/xfs_health.h

## Role in the repository

`xfs_health.h` defines the internal XFS health-tracking interface. It names health bits for filesystem-wide metadata, realtime groups, allocation groups, and inodes; groups those bits into primary, secondary, indirect, and all masks; and declares the mark, clear, measure, geometry export, and health monitor mapping functions.

## Health model

Each health domain tracks two bitsets:
- `checked`, meaning the metadata item has been examined;
- `sick`, meaning the metadata item needs repair or had problems observed.

This supports four states: checked and sick, checked and healthy, unchecked but sick from runtime evidence, and unchecked with no observed issue.

The comments classify evidence as:
- primary evidence, directly indicating a problem in that metadata group;
- secondary evidence, side effects related to primary problems;
- indirect evidence, where another group is implicated but only indirect state remains.

## Health domains

Filesystem-wide sickness bits cover summary counters, quotas, quota counts, link counts, metadata directory tree, and metadata path health.

Realtime group bits cover group superblock, bitmap, summary, realtime rmap btree, and realtime refcount btree.

Allocation group bits cover AG superblock, AGF, AGFL, AGI, bnobt, cntbt, inobt, finobt, rmapbt, refcountbt, and bad inodes observed during inactivation.

Inode bits cover inode core, data/attr/CoW bmap btrees, directory, xattrs, symlink remote targets, parent pointers, zapped data/attr/dir/symlink state, inactivation propagation suppression, and directory tree structure.

## Public interface

The header declares functions to mark filesystem, group, and inode metadata sick, corrupt, or healthy, and to measure sickness:
- `xfs_fs_mark_*`
- `xfs_group_mark_*`
- `xfs_inode_mark_*`

It also declares targeted helpers such as `xfs_bmap_mark_sick`, `xfs_btree_mark_sick`, `xfs_dirattr_mark_sick`, and `xfs_da_mark_sick`.

Geometry and userspace export helpers include `xfs_fsop_geom_health`, `xfs_ag_geom_health`, `xfs_rtgroup_geom_health`, and `xfs_bulkstat_health`. Health monitor mask translation functions convert internal masks to exported event masks.

## Inline helpers

The header provides convenience predicates for testing health:
- `xfs_fs_has_sickness`
- `xfs_group_has_sickness`
- `xfs_ag_has_sickness`
- `xfs_rtgroup_has_sickness`
- `xfs_inode_has_sickness`
- `xfs_fs_is_healthy`
- `xfs_inode_is_healthy`

`xfs_metadata_is_sick` classifies `-EFSCORRUPTED` and `-EFSBADCRC` as metadata health errors.

## Important invariants

- Runtime corruption reports set sick bits without necessarily setting checked bits.
- Scrub/fsck-style confirmed corruption sets both sick and checked.
- Successful repair clears sick and sets checked.
- Some inode zapped bits are separate from primary sickness and must be preserved in `XFS_SICK_INO_ALL`.
- `XFS_SICK_INO_FORGET` is secondary state used to avoid AG health propagation during inactivation.
