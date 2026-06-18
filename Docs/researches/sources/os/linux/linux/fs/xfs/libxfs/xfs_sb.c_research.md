# File Research: sources/os/linux/linux/fs/xfs/libxfs/xfs_sb.c

## Purpose

`xfs_sb.c` implements XFS superblock validation, endian conversion, buffer verification, mount-time geometry setup, superblock logging/syncing, secondary superblock handling, filesystem geometry reporting, stripe validation, and realtime geometry helpers.

## Main Content

- Validates supported superblock versions:
  - V5 feature compatibility requirements.
  - V4 supported feature bits.
  - Required V4 directory and unwritten extent support.
- Converts superblock version fields into in-core feature flags.
- Validates feature masks during read and write verification.
- Validates realtime geometry:
  - Realtime extent size bounds.
  - Realtime block/extent/bitmap/summary consistency.
  - Zoned realtime constraints.
  - RT group count/size/log consistency.
  - RT groups requiring exchange-range support.
- Validates common superblock fields:
  - Magic, feature masks, block/sector/inode geometry.
  - Log device placement and size.
  - AG count/block math.
  - quota flag compatibility.
  - metadir padding and RT group feature fields.
  - stripe geometry.
- Converts quota fields between legacy on-disk and in-core layouts.
- Converts `struct xfs_dsb` to/from `struct xfs_sb`, including metadir, rtgroup, metauuid, and zoned fields.
- Provides read/write verifier operations and quiet probe verifier operations.
- Computes cached mount geometry:
  - AG and RT group block counts/logs/masks.
  - realtime bitmap block payload size.
  - btree min/max records for alloc, bmap, rmap, realtime rmap, refcount, and realtime refcount btrees.
  - allocation set-aside and AG usable limits.
- Logs and syncs the primary superblock, including lazy counter snapshots and realtime free extent counters.
- Updates secondary superblocks.
- Synchronously writes superblock buffers and optionally logs/writes the realtime superblock.
- Fills `xfs_fsop_geom` ABI structures through version 5.
- Reads and allocates secondary superblock buffers.
- Validates stripe geometry with optional mount-option repair.
- Computes realtime summary log (`rextslog`) and realtime group block log (`rgblklog`).

## Key Interfaces and Invariants

- V5 filesystems must have all required historical V4 feature flags set because runtime code still checks them.
- Unknown read-only compatible features require read-only mount; unknown incompatible features reject mount.
- Write verification treats unknown feature bits as memory corruption because read verification should have rejected them.
- Metadir filesystems store quota metadata outside legacy superblock quota inode fields.
- Metadir filesystems force legacy realtime bitmap/summary inode fields to `NULLFSINO` in core and zero on disk.
- `sb_bad_features2` is kept in sync with `sb_features2` when writing.
- RT group filesystems require `sb_rgcount == ceil(sb_rextents / sb_rgextents)`.
- Zoned realtime filesystems require uniform zone capacity and no free-extent superblock counter.
- Secondary superblock update errors are logged but do not abort updates for later AGs.
- `xfs_sync_sb_buf` can hold and write both primary and realtime superblock buffers.

## Dependencies

Depends on XFS format definitions, mount state, btree geometry helpers, allocation/rmap/refcount/realtime helpers, log and transaction APIs, health tracking, buffer verifiers, and user ABI geometry structures.
