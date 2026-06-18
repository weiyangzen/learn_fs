# File Research: sources/os/linux/linux-stable/fs/lockd/share.h

Defines lockd DOS share-management data and server-side share operation prototypes.

Contents:
- `LOCKD_SHARE_SVID` synthetic owner id for share lockowner lookup.
- `struct nlm_share` links a share to host, file, owner handle, access mode, and deny mode.
- Declares `nlmsvc_share_file()`, `nlmsvc_unshare_file()`, and `nlmsvc_traverse_shares()`.

This header is used by server-side lockd share handling, while the implementation is outside this group.
