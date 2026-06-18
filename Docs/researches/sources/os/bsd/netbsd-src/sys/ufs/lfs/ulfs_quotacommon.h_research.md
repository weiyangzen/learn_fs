# File Research: sources/os/bsd/netbsd-src/sys/ufs/lfs/ulfs_quotacommon.h

Read completely: 98 lines.

Defines quota constants and conversion helpers common to quota1 and quota2.

Shared definitions:
- `INITQFNAMES` supplies string names for user and group quota types.
- `quota_idtype_to_ulfs()` maps filesystem-independent `QUOTA_IDTYPE_USER/GROUP` to `ULFS_USRQUOTA/ULFS_GRPQUOTA`.
- `quota_idtype_from_ulfs()` maps ULFS quota type constants back to public quota id types.
- Kernel builds declare `lfs_dqinit()`, `lfs_dqreinit()`, and `lfs_dqdone()`.

Role:
- Keeps quota1 and quota2 aligned on the meaning of user/group quota type indices.
- Avoids duplicating the global dquot subsystem init prototypes in format-specific headers.

Risks and notes:
- Conversion helpers return `-1` for unsupported id types; callers must check before indexing quota arrays.
- The helpers are excluded for host tool builds with `HAVE_NBTOOL_CONFIG_H`.
