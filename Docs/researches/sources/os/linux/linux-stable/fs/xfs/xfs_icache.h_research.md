# File Research: sources/os/linux/linux-stable/fs/xfs/xfs_icache.h

## Purpose

Declares the inode-cache, reclaim, blockgc, and inodegc APIs exported by `xfs_icache.c`.

## Main Types

- `struct xfs_icwalk`
  - Public scan parameters for blockgc-style inode walks.
  - Includes filter flags, uid/gid/project id filters, minimum file size, and scan limit.

## Main Flags

- `XFS_ICWALK_FLAG_SYNC`
- `XFS_ICWALK_FLAG_UID`
- `XFS_ICWALK_FLAG_GID`
- `XFS_ICWALK_FLAG_PRID`
- `XFS_ICWALK_FLAG_MINFILESIZE`
- `XFS_ICWALK_FLAGS_VALID`

## Main API

- Inode lookup/allocation:
  - `xfs_iget`
  - `xfs_inode_alloc`
  - `xfs_inode_free`
- Reclaim:
  - `xfs_reclaim_worker`
  - `xfs_reclaim_inodes`
  - `xfs_reclaim_inodes_count`
  - `xfs_reclaim_inodes_nr`
  - `xfs_inode_mark_reclaimable`
- Blockgc:
  - `xfs_blockgc_free_dquots`
  - `xfs_blockgc_free_quota`
  - `xfs_blockgc_free_space`
  - `xfs_blockgc_flush_all`
  - EOF/COW tag setters and clearers
  - `xfs_blockgc_worker`
  - `xfs_blockgc_stop`
  - `xfs_blockgc_start`
- Inodegc:
  - `xfs_inodegc_worker`
  - `xfs_inodegc_push`
  - `xfs_inodegc_flush`
  - `xfs_inodegc_stop`
  - `xfs_inodegc_start`
  - `xfs_inodegc_register_shrinker`

## Important Invariants

- `xfs_iget` flags distinguish creation, untrusted lookup, don't-cache lookup, incore-only lookup, and no-retry lookup.
- Synchronous blockgc callers must avoid holding inode IO/MMAP locks, as documented by the implementation.
- Inodegc and blockgc lifecycle control is mount-level state and must coordinate with unmount.

## Research Notes

This header is the public in-kernel surface for inode cache users. Most behavior is implemented in `xfs_icache.c`; the header mostly communicates scan-filter contracts and lifecycle entry points.
