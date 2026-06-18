# File Research: sources/os/linux/linux-stable/fs/ntfs/quota.c

`quota.c` implements quota invalidation for NTFS volumes.

Key function:
- `ntfs_mark_quotas_out_of_date()` marks the default quota control entry in `$Quota/$Q` as out of date so Windows will rescan and rebuild quota entries later.

Behavior:
- Returns success immediately if the volume is already marked quota-out-of-date.
- Requires both `vol->quota_ino` and `vol->quota_q_ino` to be open.
- Locks the quota index inode, opens the `$I30` index context, looks up `QUOTA_DEFAULTS_ID`, validates entry size and `QUOTA_VERSION`, and inspects quota flags.
- If quota tracking is enabled/requested or pending deletes exist, sets `QUOTA_FLAG_OUT_OF_DATE` and marks the index entry dirty.
- Sets the in-memory volume flag `NVolSetQuotaOutOfDate()` so the operation is not repeated.

Dependencies:
- Quota layout definitions from included headers.
- Index helpers from `index.h`.
- Volume state flags from `volume.h`/`ntfs.h`.

Error handling:
- Logs missing quota inodes, failed context lookup, missing defaults entry, invalid entry size, unsupported version, or lookup failure.
- Ensures index context and inode lock are released on error.
