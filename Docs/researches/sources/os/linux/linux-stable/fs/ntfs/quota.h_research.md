# File Research: sources/os/linux/linux-stable/fs/ntfs/quota.h

`quota.h` declares the quota invalidation API.

Contents:
- Includes `volume.h`.
- Declares `bool ntfs_mark_quotas_out_of_date(struct ntfs_volume *vol);`.

Design role:
- Provides a narrow interface for callers that need to flag NTFS quota metadata as stale after metadata changes.
