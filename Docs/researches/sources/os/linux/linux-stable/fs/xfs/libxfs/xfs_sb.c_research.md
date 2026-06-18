# File Research: sources/os/linux/linux-stable/fs/xfs/libxfs/xfs_sb.c

## Purpose

Implements XFS superblock validation, conversion between disk and in-core formats, buffer verifiers, mount-time geometry initialization, superblock logging/syncing, secondary superblock handling, filesystem geometry reporting, and stripe/realtime geometry validation.

## Main Responsibilities

- Validates supported v4/v5 superblock versions and feature masks.
- Converts superblock feature bits into in-core feature flags.
- Validates realtime geometry, including rtgroups and zoned realtime constraints.
- Validates stripe geometry and core allocation group geometry.
- Converts superblocks:
  - `xfs_sb_from_disk`
  - `xfs_sb_to_disk`
- Handles quota inode compatibility conversion for older formats.
- Defines superblock buffer ops:
  - `xfs_sb_buf_ops`
  - `xfs_sb_quiet_buf_ops`
- Initializes mount-derived geometry:
  - AG geometry
  - RTG geometry
  - btree max/min record counts
  - realtime extent-size caches
- Logs and syncs the primary superblock and optional realtime superblock.
- Updates secondary superblocks.
- Reports user-visible filesystem geometry through `xfs_fs_geometry`.

## Rtgroup and Zoned Integration

This file validates and initializes newer realtime fields:
- `sb_rgcount`
- `sb_rgextents`
- `sb_rgblklog`
- `sb_rtstart`
- `sb_rtreserved`

Rtgroup validation requires:
- nonzero realtime extent size
- bounded realtime group size
- group count covering all realtime extents
- exchange-range support
- expected `rgblklog`

Zoned validation requires:
- `sb_frextents == 0`
- realtime start not overlapping data blocks
- reserved realtime blocks below total realtime blocks
- uniform realtime group alignment

## Important Invariants

- V5 filesystems must carry required legacy feature flags because much code checks those flags directly.
- Unknown read-only compatible features block read-write mounts.
- Unknown incompatible features block mounting.
- Primary superblock summary counters are sanity-checked on write.
- Metadir filesystems zero classic realtime bitmap and summary inode fields on disk.
- Metadir filesystems treat quota inodes differently and store quota metadata in the metadir.
- Realtime summary block sizing changes when metadir/rtgroups are enabled.

## Dependencies

- Calls into allocation, inode, rmap, refcount, realtime bitmap, rtrmap, and rtrefcount geometry helpers.
- `xfs_sync_sb_buf` can update the realtime superblock through `xfs_log_rtsb`.
- User-visible geometry flags reflect feature helpers from the mount structure.

## Research Notes

This is the main format gatekeeper. New rtgroup, metadir, rtrmapbt, rtrefcountbt, and zoned behavior must remain consistent with validation here or mount-time rejection and incorrect reservation sizing can occur.
