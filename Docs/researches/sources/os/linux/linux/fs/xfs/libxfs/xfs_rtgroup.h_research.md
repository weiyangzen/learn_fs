# File Research: sources/os/linux/linux/fs/xfs/libxfs/xfs_rtgroup.h

## Purpose

`xfs_rtgroup.h` declares the realtime group abstraction, metadata inode slots, reference wrappers, address conversion helpers, validation helpers, locking flags, lifecycle APIs, and realtime superblock helper APIs.

## Main Content

- Defines `enum xfs_rtg_inodes` for per-RTG bitmap, summary, rmap, and refcount metadata inodes.
- Defines `struct xfs_rtgroup`:
  - Embedded generic `struct xfs_group`.
  - Metadata inode pointers.
  - Realtime extent count.
  - Union for bitmap summary cache or zoned open-zone tracking.
  - Zoned garbage-collection operation count.
- Defines `XFS_RTG_FREE` xarray mark for free zoned RT groups.
- Provides inline accessors for mount, group number, group size, and metadata inodes.
- Wraps generic group passive and active reference helpers for RT groups.
- Provides RT group iteration helpers.
- Defines RT group block validation and conversion helpers:
  - `xfs_verify_rgbno`, `xfs_verify_rgbext`.
  - `xfs_rgbno_to_rtb`, `xfs_rtb_to_rgno`, `xfs_rtb_to_rgbno`.
  - `xfs_rtx_to_rgbno`.
  - `xfs_rtb_to_daddr`, `xfs_daddr_to_rtb`.
- Declares RT group lifecycle, geometry, locking, metadata inode, and realtime superblock APIs when `CONFIG_XFS_RT` is enabled.
- Provides no-op stubs for many RT helpers when realtime support is disabled.
- Provides helpers for raw RT group sizing and RT group count to raw filesystem block conversion.

## Key Interfaces and Invariants

- `xfs_verify_rgbno` and `xfs_verify_rgbext` require rtgroups-enabled filesystems.
- Dense RT group device address conversion differs from filesystems with zone/daddr gaps.
- `xfs_rtgroup_raw_size` includes address gaps when `XFS_SB_FEAT_INCOMPAT_ZONE_GAPS` is active.
- RT group metadata inode paths are generated as `<rgno>.<shortname>`.
- Duplicate `xfs_rtginode_irele` declarations are present but harmless.

## Dependencies

Depends on `xfs_group.h`, XFS mount geometry, group xarray state, realtime feature predicates, metadata inode types, and buffer/inode types declared elsewhere.
