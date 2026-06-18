# File Research: sources/local-fs/xfsprogs/libxfs/xfs_sb.h

This header declares the superblock functions implemented in `xfs_sb.c`. It is a compact interface for logging/syncing superblocks, mount-time geometry setup, disk/incore conversion, quota conversion, version/feature validation, geometry export, secondary superblock I/O, stripe and realtime geometry validation, and realtime geometry helpers.

Important declarations for this group are `xfs_sync_sb_buf` with its `update_rtsb` flag, `xfs_sb_mount_rextsize`, `xfs_mount_sb_set_rextsize`, `xfs_validate_rt_geometry`, `xfs_compute_rextslog`, and `xfs_compute_rgblklog`. Those functions connect superblock state to realtime group sizing, realtime superblock updates, and mount-time precomputed rtgroup geometry.

The header also sets `XFS_FS_GEOM_MAX_STRUCT_VER` to 5, matching the geometry export path that includes rtgroup and zoned realtime fields.
