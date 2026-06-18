# File Research: sources/os/linux/linux/fs/xfs/libxfs/xfs_quota_defs.h

This header defines quota-related shared types, flags, reservations, helpers, and quota inode metadata-directory interfaces.

Key contents:
- `xfs_qcnt_t` as a 64-bit quota counter/limit type.
- `xfs_dqtype_t` as an 8-bit quota type.
- String tables for quota types and dquot flags.
- Dirty flag `XFS_DQFLAG_DIRTY`.
- `XFS_DQUOT_LOGRES`, sized for worst-case transactions modifying up to six dquots plus log format items.
- Quota enabled/enforced predicate macros for user, group, and project quotas.
- Non-persistent `XFS_QMOPT_*` operation flags for quota selection, reservation, accounting fields, and inheritance.
- Transaction dquot modification aliases.
- Quota option masks for all quota types and block reservation flags.
- Declarations for dquot verification, repair, timestamp conversion, and chunk sizing.
- Quota inode helpers for metadir path/type mapping and loading/creating/linking quota inodes.

Important behavior:
- User, group, and project quota inode paths map to `"user"`, `"group"`, and `"project"`.
- Quota inode metafile types map to `XFS_METAFILE_USRQUOTA`, `XFS_METAFILE_GRPQUOTA`, and `XFS_METAFILE_PRJQUOTA`.
- Header notes that `XFS_QMOPT_*` values are not persistent ABI and may change between versions.

Integration:
- Shares quota constants with kernel and userspace source trees.
- Depends on quota flags from `xfs_log_format.h`.
- Connects quota inode handling to metadir/metafile infrastructure.

Risk notes:
- `XFS_DQUOT_LOGRES` encodes worst-case transaction reservation assumptions.
- Operation flags must not be stored persistently.
- Invalid quota type reaches assertions in inline path/metafile-type helpers.
