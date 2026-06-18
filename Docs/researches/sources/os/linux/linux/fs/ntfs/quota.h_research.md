# File Research: sources/os/linux/linux/fs/ntfs/quota.h

Header for NTFS quota handling.

Exports:
- `ntfs_mark_quotas_out_of_date(struct ntfs_volume *vol)`.

Role:
- Provides the quota out-of-date marker used by mount/remount or metadata-changing paths that need Windows to rescan quota state.
