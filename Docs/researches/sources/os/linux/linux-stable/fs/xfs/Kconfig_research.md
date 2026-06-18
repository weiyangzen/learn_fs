# File Research: sources/os/linux/linux-stable/fs/xfs/Kconfig

## Purpose

This file declares Linux kernel configuration options for building XFS and optional XFS features.

## Main Configuration Items

- `XFS_FS`
  - Tristate filesystem support.
  - Depends on `BLOCK`.
  - Selects `EXPORTFS`, `CRC32`, and `FS_IOMAP`.
- Deprecated format support:
  - `XFS_SUPPORT_V4` for old non-CRC V4 filesystems, default `n`.
  - `XFS_SUPPORT_ASCII_CI` for deprecated ASCII case-insensitive filesystems, default `n`.
  - Both document September 2025 default-off status and September 2030 planned removal.
- Feature options:
  - `XFS_QUOTA` selects `QUOTACTL`.
  - `XFS_POSIX_ACL` selects `FS_POSIX_ACL`.
  - `XFS_RT` enables realtime subvolume support and defaults to `BLK_DEV_ZONED`.
- Internal feature switches:
  - `XFS_DRAIN_INTENTS`, `XFS_LIVE_HOOKS`, `XFS_MEMORY_BUFS`, `XFS_BTREE_IN_MEM`.
- Online maintenance:
  - `XFS_ONLINE_SCRUB` depends on `TMPFS && SHMEM` and selects live hooks, drain intents, and memory buffers.
  - `XFS_ONLINE_SCRUB_STATS` depends on scrub and debugfs.
  - `XFS_ONLINE_REPAIR` depends on scrub and selects in-memory btrees.
- Debug controls:
  - `XFS_WARN`
  - `XFS_DEBUG`
  - `XFS_DEBUG_EXPENSIVE`
  - `XFS_ASSERT_FATAL`

## Important Semantics

- V4 and ASCII case-insensitive formats are treated as security/robustness liabilities and are opt-in.
- Realtime support is mandatory for zoned block device support.
- Online repair requires richer metadata such as reverse mappings and parent pointers, as documented in help text.
- `XFS_WARN` provides lighter checks than full debug, while `XFS_DEBUG` changes behavior through assertions and sanity checks.

## Research Notes

This Kconfig file defines the build-time feature surface for the XFS files referenced by this group. It explains which code paths in the Makefile and allocator/AG code are conditional, especially quota, ACL, realtime/zoned support, online scrub/repair, and debug-only allocator checks.
