# File Research: sources/local-fs/xfsprogs/libxfs/xfs_quota_defs.h

## Role

This header defines quota-related shared types, flags, reservation constants, option flags, helper mappings, and quota inode metadir helpers used by kernel and userspace XFS code.

## Main Types And Flags

- `xfs_qcnt_t` is a 64-bit quota counter/limit type.
- `xfs_dqtype_t` is the quota type id.
- `XFS_DQTYPE_STRINGS` maps user, project, group, and bigtime quota type names.
- `XFS_DQFLAG_DIRTY` identifies dirty dquots.

`XFS_DQUOT_LOGRES` reserves space for worst-case transactions that can modify up to six dquots plus their log format items.

## Mount Quota Tests

Macros test whether quota accounting or enforcement is active for user, group, project, or any quota type:

- `XFS_IS_QUOTA_ON`
- `XFS_IS_UQUOTA_ON`
- `XFS_IS_PQUOTA_ON`
- `XFS_IS_GQUOTA_ON`
- enforcement variants for each quota type

## Quota Operation Flags

`XFS_QMOPT_*` flags identify requested quota types, forced reservations, superblock version updates, reserved regular/realtime blocks, block and inode count modifications, delayed counters, and inherited dqalloc behavior.

Transaction-facing aliases map quota modification meanings to `XFS_TRANS_DQ_*` constants.

## Verification And Conversion Declarations

The header declares dquot and dquot-block verification/repair helpers, dquots-per-chunk calculation, and bigtime quota expiration conversion helpers.

## Quota Inode Helpers

`xfs_dqinode_path` maps quota type to metadir path names: `user`, `group`, or `project`.

`xfs_dqinode_metafile_type` maps quota type to metadata file type: user, group, or project quota.

The header declares helpers to derive health sick masks, load quota inodes from metadir, create/link metadir quota inodes, and create/load the quota parent directory.

## Dependencies

This header depends on quota status bits from log format, dquot disk structures, metadata file type definitions, transactions, inodes, and mount quota flags.

## Research Notes

The quota option flags are internal and explicitly not persistent. The path/metafile mapping functions connect traditional quota inode concepts to the newer metadata directory tree.
