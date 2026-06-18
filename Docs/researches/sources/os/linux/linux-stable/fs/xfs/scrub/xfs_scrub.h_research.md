# File Research: sources/os/linux/linux-stable/fs/xfs/scrub/xfs_scrub.h

## Purpose

Declares XFS online scrub ioctl entry points, with stubs when online scrub is disabled.

## Key Contents

- When `CONFIG_XFS_ONLINE_SCRUB` is enabled:
  - `xfs_ioc_scrub_metadata`
  - `xfs_ioc_scrubv_metadata`
- When disabled, both ioctl helpers expand to `-ENOTTY`.

## Research Notes

This header is the external switch point between generic ioctl handling and the online scrub implementation.
