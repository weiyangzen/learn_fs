# File Research: sources/os/linux/linux-stable/fs/xfs/xfs_fsops.c

## Purpose

Implements filesystem-level operations for growing/shrinking data space, changing inode percentage limits, reserving global/per-AG metadata blocks, and forcing filesystem shutdown.

## Main Responsibilities

- Initializes new AG headers during growfs with delayed-write buffer lists.
- Grows or partially shrinks the data section:
  - validates new block count
  - probes new device size
  - checks realtime geometry constraints
  - computes AG deltas
  - initializes new perag structures
  - extends or shrinks the last AG
  - updates superblock counters transactionally
  - refreshes low-space thresholds and allocation set-aside
  - reinitializes per-AG reservations when needed
- Rejects unsupported full-AG shrink and log movement operations.
- Changes `sb_imax_pct` transactionally.
- Provides locked/capability-checked growfs ioctl entry points:
  - `xfs_growfs_data`
  - `xfs_growfs_log`
- Reserves and unreserves global free block counters through `xfs_reserve_blocks`.
- Implements `xfs_fs_goingdown` for user-requested shutdown modes.
- Implements `xfs_do_force_shutdown`, including one-time shutdown transition, log shutdown, diagnostics, fserror, and healthmon reporting.
- Reserves and frees per-AG and realtime metadata reserve pools:
  - `xfs_fs_reserve_ag_blocks`
  - `xfs_fs_unreserve_ag_blocks`

## Important Invariants

- Growfs operations require `CAP_SYS_ADMIN` and `m_growlock`.
- Data section cannot grow when an internal realtime section exists.
- Filesystems cannot be shrunk below two AGs.
- Superblock updates are committed synchronously after new AG headers are written.
- Lazy superblock counters are logged during shrink/grow to keep verifier-visible counters coherent.
- `-ENOSPC` during metadata reservation after grow is not treated as growfs failure.
- Force shutdown is atomic; only the first caller performs full reporting/log shutdown.

## Dependencies

- Uses AG header initialization, perag management, AG reservation, superblock logging, transaction, realtime geometry, realtime btree maxlevel, metafile reservation, and health monitor subsystems.
- Uses block device freeze/thaw for default goingdown behavior.

## Research Notes

This file is the high-level administrative operations layer. It is conservative: log growth/movement is still unsupported, full-AG shrink is rejected, and post-grow reservation failures are distinguished from structural grow failures.
