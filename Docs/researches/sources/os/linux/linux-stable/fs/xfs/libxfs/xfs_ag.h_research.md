# File Research: sources/os/linux/linux-stable/fs/xfs/libxfs/xfs_ag.h

## Purpose

This header defines the in-core XFS per-allocation-group structure, per-AG reservation structure, AG operational state helpers, per-AG reference helpers, geometry validation helpers, AG iteration macros, and AG grow/shrink/reporting declarations.

## Key Types

- `struct xfs_ag_resv`
  - Tracks per-AG reservation state:
    - `ar_orig_reserved`
    - `ar_reserved`
    - `ar_asked`
- `struct xfs_perag`
  - Embeds `struct xfs_group`.
  - Caches AGF-derived state:
    - bno/cnt/rmap/refcount btree levels
    - AGFL count
    - free blocks
    - longest free extent
    - btree block count
  - Caches AGI-derived inode counts.
  - Stores inode allocation search hints.
  - Holds metadata and rmapbt reservations.
  - Stores precomputed minimum and maximum valid AG inode numbers.
  - Kernel-only fields include inode cache locking/radix tree, filestream count, reclaim cursor, blockgc work, and repair alternate btree levels.

## Operational State

Defines atomic bit positions and inline test helpers for:

- AGF initialized
- AGI initialized
- AG prefers metadata
- AG allows inodes
- AGFL needs reset

## Reference Helpers

- Passive references:
  - `xfs_perag_get`
  - `xfs_perag_hold`
  - `xfs_perag_put`
- Active references:
  - `xfs_perag_grab`
  - `xfs_perag_rele`
- Iteration:
  - `xfs_perag_next_range`
  - `xfs_perag_next_from`
  - `xfs_perag_next`
  - wrap helpers/macros for allocation scans.

## Geometry Helpers

- `xfs_ag_block_count`
- `xfs_agino_range`
- `xfs_verify_agbno`
- `xfs_verify_agbext`
- `xfs_verify_agino`
- `xfs_verify_agino_or_null`
- `xfs_ag_contains_log`
- conversion helpers:
  - `xfs_agbno_to_fsb`
  - `xfs_agbno_to_daddr`
  - `xfs_agino_to_ino`

## Grow/Shrink Interfaces

Declares:

- `xfs_initialize_perag`
- `xfs_free_perag_range`
- `xfs_initialize_perag_data`
- `xfs_update_last_ag_size`
- `xfs_ag_init_headers`
- `xfs_ag_shrink_space`
- `xfs_growfs_compute_deltas`
- `xfs_ag_extend_space`
- `xfs_ag_get_geometry`

## Important Invariants

- `xfs_verify_agino` rejects inode numbers outside precomputed AG inode bounds and therefore protects static metadata space.
- Wrap iteration releases the current active per-AG reference before grabbing the next one.
- `xfs_ag_contains_log` only applies to internal-log filesystems.
- AG iteration macros are used by allocator paths to scan AGs while respecting wrap boundaries.

## Research Notes

This header is the shared contract between AG lifecycle code, allocator code, inode allocation, repair/scrub, and geometry consumers. Most allocator correctness depends on the cached `pagf_*` fields remaining synchronized with AGF buffer changes.
