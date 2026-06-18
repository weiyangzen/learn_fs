# File Research: sources/os/linux/linux-stable/fs/xfs/libxfs/xfs_quota_defs.h

## Role
`xfs_quota_defs.h` provides quota constants, flags, reservation sizing, option masks, quota state predicates, dquot verification declarations, quota timestamp conversion declarations, and metadata-directory quota inode helpers shared by kernel and userspace XFS code.

## Main Definitions
- `xfs_qcnt_t` is a 64-bit quota counter/limit type.
- `xfs_dqtype_t` identifies user, project, group, and bigtime quota-related types.
- `XFS_DQUOT_LOGRES` estimates log reservation for worst-case dquot updates, including up to six dquots plus log format items.
- `XFS_IS_*QUOTA_*` macros test accounting and enforcement bits in mount quota flags.
- `XFS_QMOPT_*` flags select quota types, forced reservations, superblock version changes, reserved/actual block and inode counter fields, delayed counters, realtime counters, and inherited dquot behavior.
- `XFS_TRANS_DQ_*` aliases map transaction dquot modification operations to quota option bits.
- `xfs_dqinode_path` maps dquot type to metadata directory path names.
- `xfs_dqinode_metafile_type` maps dquot type to metadata file type enum values.

## Exported API
- Dquot integrity and repair: `xfs_dquot_verify`, `xfs_dqblk_verify`, `xfs_calc_dquots_per_chunk`, and `xfs_dqblk_repair`.
- Bigtime quota expiry conversion: `xfs_dquot_from_disk_ts` and `xfs_dquot_to_disk_ts`.
- Quota inode health and metadir support: `xfs_dqinode_sick_mask`, `xfs_dqinode_load`, `xfs_dqinode_metadir_create`, `xfs_dqinode_metadir_link`, `xfs_dqinode_mkdir_parent`, and `xfs_dqinode_load_parent`.

## Data and Invariants
- User, group, and project quotas can all be active simultaneously, so reservations must account for multi-dquot updates.
- Group and project quota flags retain historical “other quota” conversion constraints handled by superblock qflags conversion code, not here.
- `XFS_QMOPT_*` values are not persistent ABI values and may change between versions.
- Metadata directory quota inode helpers map quota files into named metadata files: `user`, `group`, and `project`.

## Dependencies
This header depends on dquot disk structures, log dquot format, mount quota flags from log format definitions, metadata file type definitions, and quota inode implementation elsewhere.

## Research Notes
Despite the filename, this header includes more than constants: it is the shared quota operation vocabulary for transaction accounting, metadata quota inode discovery, and dquot verification.
