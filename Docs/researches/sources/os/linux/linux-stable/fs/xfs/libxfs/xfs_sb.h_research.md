# File Research: sources/os/linux/linux-stable/fs/xfs/libxfs/xfs_sb.h

## Purpose

Declares the superblock manipulation, validation, sync, mount-geometry, secondary-superblock, and geometry-reporting APIs.

## Main API

- Logging and syncing:
  - `xfs_log_sb`
  - `xfs_sync_sb`
  - `xfs_sync_sb_buf`
- Mount setup:
  - `xfs_sb_mount_common`
  - `xfs_sb_mount_rextsize`
  - `xfs_mount_sb_set_rextsize`
- Disk conversion:
  - `xfs_sb_from_disk`
  - `xfs_sb_to_disk`
  - `xfs_sb_quota_from_disk`
- Validation and feature interpretation:
  - `xfs_sb_good_version`
  - `xfs_sb_version_to_features`
  - `xfs_validate_stripe_geometry`
  - `xfs_validate_rt_geometry`
- Geometry reporting:
  - `xfs_fs_geometry`
- Secondary superblocks:
  - `xfs_update_secondary_sbs`
  - `xfs_sb_read_secondary`
  - `xfs_sb_get_secondary`
- Realtime calculations:
  - `xfs_compute_rextslog`
  - `xfs_compute_rgblklog`

## Research Notes

This header is compact but central: it exposes format-validation and mount-geometry services used throughout libxfs and the kernel.
