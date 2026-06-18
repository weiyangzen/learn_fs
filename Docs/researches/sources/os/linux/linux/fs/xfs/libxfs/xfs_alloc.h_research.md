# File Research: sources/os/linux/linux/fs/xfs/libxfs/xfs_alloc.h

Declares XFS allocation/free-space APIs, flags, argument structures, and deferred free item structures.

Key behavior:
- Declares allocator workqueue and AGFL sizing.
- Defines `xfs_alloc_fix_freelist` flags:
  - trylock.
  - freeing mode.
  - no rmap updates.
  - no AGFL shrink.
  - check-only.
  - try busy flush.
- Defines `struct xfs_alloc_arg`, the central allocation request/result object:
  - transaction, mount, AGF buffer, perag.
  - target/result block fields.
  - min/max length, alignment, prod/mod, minleft, total.
  - AG block range constraints.
  - data type flags.
  - delayed-allocation/freelist result flags.
  - owner info and reservation type.
- Defines allocation data-type flags:
  - user data.
  - initial user data.
  - no busy extents.
- Declares free-space accounting helpers:
  - set-aside.
  - max usable.
  - longest free extent.
  - minimum freelist.
- Declares AGFL get/put, free extent, maxlevel computation, AGF logging, and AGF/AGFL readers.
- Declares allocation entry points:
  - this AG.
  - near block.
  - exact block.
  - start AG scan.
  - first AG scan.
- Declares btree lookup/get/query helpers for free-space records.
- Declares AGFL walker and `xfs_buf_to_agfl_bno` layout helper.
- Declares deferred free scheduling via `xfs_free_extent_later`.
- Defines deferred free flags:
  - skip discard.
  - realtime.
- Defines `struct xfs_extent_free_item`, the sorted deferred free list item.
- Defines EFI item flags for discard skipping, attr fork, bmap btree block, cancellation, and realtime.
- Declares autoreap schedule/cancel/commit helpers.
- Declares extent-free intent cache lifecycle.
- Declares AG length validation helper.

Important interactions:
- This header is the allocator contract consumed by bmap, rmap, refcount, AG grow/shrink, repair, and transaction code.
- Reservation type in `xfs_alloc_arg` connects allocation/free operations to per-AG reservation accounting.
