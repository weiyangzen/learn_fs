# File Research: sources/os/linux/linux/fs/xfs/xfs_health.c

Implements XFS health/sickness state tracking for filesystem-wide metadata, AG/realtime-group metadata, and per-inode metadata, plus translation to ioctl and health-monitor masks.

Key logic:
- Unmount reporting:
  - `xfs_health_unmount` scans AGs, realtime groups, and filesystem-wide sickness, warns about unfixed corruption, and clears `FS_COUNTERS` sickness in the special case where a dirty-log repair recommendation would be harmful.
- Filesystem health:
  - `xfs_fs_mark_sick`, `xfs_fs_mark_corrupt`, `xfs_fs_mark_healthy`, and `xfs_fs_measure_sickness` update `m_fs_sick`/`m_fs_checked` under `m_sb_lock`, report metadata errors, and emit health-monitor events.
- Group health:
  - `xfs_agno_mark_sick`, `xfs_rgno_mark_sick`, `xfs_group_mark_sick`, `xfs_group_mark_corrupt`, `xfs_group_mark_healthy`, and `xfs_group_measure_sickness` manage `xg_sick`/`xg_checked` under group state locks with AG vs realtime-group mask validation.
- Inode health:
  - `xfs_inode_mark_sick`, `xfs_inode_mark_corrupt`, `xfs_inode_mark_healthy`, and `xfs_inode_measure_sickness` manage `i_sick`/`i_checked`, clear `I_DONTCACHE` so sickness reports are retained, report file metadata errors when possible, and notify health monitoring.
- Ioctl mask translation:
  - Static maps translate internal sick masks to `XFS_FSOP_GEOM`, `XFS_AG_GEOM`, `XFS_RTGROUP_GEOM`, and bulkstat sick/checked masks.
  - `xfs_fsop_geom_health`, `xfs_ag_geom_health`, `xfs_rtgroup_geom_health`, and `xfs_bulkstat_health` fill public health fields.
  - `xfs_healthmon_fs_mask`, `xfs_healthmon_perag_mask`, `xfs_healthmon_rtgroup_mask`, and `xfs_healthmon_inode_mask` translate masks for event reporting.
- Corruption classification helpers:
  - `xfs_bmap_mark_sick` maps data/attr/COW fork bmap corruption to inode sickness.
  - `xfs_btree_mark_sick` marks inode bmap or group btree sickness depending on cursor type.
  - `xfs_dirattr_mark_sick` and `xfs_da_mark_sick` classify directory vs xattr btree corruption.

This file is the central state machine for “observed corrupt”, “checked corrupt”, and “healthy” metadata status, bridging internal error detection, fsnotify/fserror, userspace geometry/bulkstat reporting, and health monitor events.
