# File Research: sources/os/linux/linux/fs/xfs/libxfs/xfs_ag_resv.c

Implements per-AG block reservations for metadata structures that must be able to grow without hitting ENOSPC.

Key behavior:
- Explains the reservation model:
  - reserve blocks per AG for metadata btree growth.
  - hide reservation space from global free-block accounting.
  - track per-AG reserved counters in memory.
  - account rmapbt specially because it lives in free space/AGFL-owned space.
- `xfs_ag_resv_critical` reports low-reservation conditions for metadata and rmapbt reservations using 10% and max-btree-height thresholds, plus error injection.
- `xfs_ag_resv_needed` reports blocks reserved for other reservation classes that must not be allocated away.
- `xfs_ag_resv_free` releases rmapbt and metadata reservations back to `fdblocks`, restoring `m_ag_max_usable` for AG 0.
- `__xfs_ag_resv_init`:
  - normalizes `ask >= used`.
  - computes hidden space by reservation type.
  - decrements global free blocks.
  - adjusts `m_ag_max_usable` for AG 0.
  - records asked, original reserved, and currently reserved values.
- `xfs_ag_resv_init` creates:
  - metadata reservations for refcountbt and finobt needs.
  - rmapbt reservations.
  - fallback behavior if finobt reservation cannot be fully established on older filesystems.
  - AGF initialization when active reservations exist.
  - `-ENOSPC` if reservations exceed AG free space.
- `xfs_ag_resv_alloc_extent` consumes reservation counters and updates transaction superblock accounting according to reservation type.
- `xfs_ag_resv_free_extent` replenishes reservation counters when blocks are freed and accounts leftover blocks to normal free space.

Important interactions:
- Uses reserve calculators from refcountbt, finobt, and rmapbt code.
- Allocation paths call reservation helpers after allocating or freeing extents.
- AG shrink temporarily frees and then reinitializes reservations to validate the new geometry.
