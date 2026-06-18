# File Research: sources/os/linux/linux/fs/xfs/scrub/xfs_scrub.h

Public ioctl-facing declarations for XFS online scrub.

Key elements:
- When `CONFIG_XFS_ONLINE_SCRUB` is disabled, `xfs_ioc_scrub_metadata` and `xfs_ioc_scrubv_metadata` are macros returning `-ENOTTY`.
- When online scrub is enabled, declares both ioctl entry points.

Dependencies:
- Used by XFS ioctl code to gate scrub support at compile time.

Research notes:
- The header provides a hard disabled behavior without requiring callers to add their own `#ifdef` blocks.
