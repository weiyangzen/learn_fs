# File Research: sources/os/linux/linux-stable/fs/jfs/jfs_discard.h

Small discard interface header.

Exports:
- Forward declaration for `struct fstrim_range`.
- `jfs_issue_discard()` for issuing device discards.
- `jfs_ioc_trim()` for FITRIM handling.

Integration:
- Used by ioctl, dmap free/discard paths, and related JFS block management code.
