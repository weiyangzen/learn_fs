# File Research: sources/os/linux/linux/fs/ntfs/quota.c

Handles marking NTFS quota metadata out of date.

Key function:
- `ntfs_mark_quotas_out_of_date()` opens the quota `$Q` index on `vol->quota_q_ino`, finds the defaults entry `QUOTA_DEFAULTS_ID`, validates entry size and `QUOTA_VERSION`, and sets `QUOTA_FLAG_OUT_OF_DATE` when quota tracking/request/pending-delete state requires it.

Behavior:
- Skips work if the volume already has `NVolQuotaOutOfDate()`.
- Requires `vol->quota_ino` and `vol->quota_q_ino`.
- Marks the index entry dirty after changing flags.
- Sets the in-memory volume flag so remount paths do not repeat the operation.

Failure behavior:
- Returns `false` on missing quota inodes, lookup failure, invalid entry size, or unsupported quota version.
- Always releases index context and unlocks `quota_q_ino` on error paths.
