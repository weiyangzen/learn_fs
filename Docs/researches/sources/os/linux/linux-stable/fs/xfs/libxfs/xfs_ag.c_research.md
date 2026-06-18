# File Research: sources/os/linux/linux-stable/fs/xfs/libxfs/xfs_ag.c

## Purpose

This file manages XFS allocation group lifecycle, in-core per-AG initialization, AG geometry, growfs/shrink operations, new AG header initialization, and AG geometry reporting.

## Main Responsibilities

- Initializes per-AG runtime data and filesystem summary counters.
- Allocates and frees in-core `xfs_perag` objects.
- Computes AG block counts and valid per-AG inode ranges.
- Initializes AG headers and root btree blocks for growfs.
- Extends or shrinks the final AG during filesystem resize.
- Reports AG geometry and health to callers.

## Key Functions

- `xfs_initialize_perag_data`
  - Reads each AGF and AGI to populate per-AG state.
  - Rebuilds in-core superblock counters for free blocks, free inodes, allocated inodes, AGFL blocks, and btree blocks.
  - Detects impossible counter values and marks filesystem counters sick.
- `xfs_initialize_perag`
  - Allocates new per-AG structures from `orig_agcount` to `new_agcount`.
  - Updates inode allocation limits and preallocated AG metadata block count.
- `xfs_free_perag_range`
  - Frees per-AG group objects and cancels kernel-only delayed blockgc work.
- `xfs_ag_block_count`, `xfs_agino_range`, `xfs_update_last_ag_size`
  - Maintain geometry for normal and shortened final AGs.
- `xfs_ag_init_headers`
  - Creates uncached buffers for new AG headers and btree roots during grow.
  - Initializes SB, AGF, AGFL, AGI, BNOBT, CNTBT, INOBT, optional FINOBT, RMAPBT, and REFCBT roots.
- `xfs_ag_shrink_space`
  - Shrinks the final AG by allocating the tail extent exactly, updating AGI/AGF lengths, reinitializing reservations, and updating per-AG geometry.
- `xfs_ag_extend_space`
  - Extends final AG length, updates AGI/AGF, frees new space into allocation btrees, and updates rmap state with skip-update owner info.
- `xfs_growfs_compute_deltas`
  - Computes new block delta and AG count while respecting minimum AG size and maximum AG number.
- `xfs_ag_get_geometry`
  - Reads AGI/AGF, reports inode/free block counters, subtracts per-AG reserved space, and annotates health.

## Header Initialization Details

- Free space btree roots start with records covering space after static AG metadata and excluding internal log space if present.
- RMAP root initialization records static metadata, btree roots, inode btrees, optional refcount root, and internal log ownership.
- AGF initialization sets free block, longest extent, root pointers, levels, AGFL counters, optional rmap/refcount fields, and UUID.
- AGFL initialization sets v5 headers and fills block number slots with `NULLAGBLOCK`.
- AGI initialization sets inode btree roots, finobt roots if enabled, unlink buckets, and inode btree block counters.

## Important Invariants and Edge Cases

- Resize operations apply only to the last AG.
- Shrink temporarily frees per-AG reservations so the exact tail allocation cannot be blocked by reservation accounting.
- Shrink must preserve AGI/AGF lock ordering through transaction rolls.
- If per-AG reservation reinitialization fails after shrink changes, the code rolls back or forces shutdown for in-core corruption.
- Grow uses uncached buffers because new AG headers may be beyond the current filesystem address space and cached lookup would trip EOFS checks.
- Geometry calculations exclude static metadata and align inode ranges to inode cluster alignment.

## Dependencies

- Allocation and free-space btrees, inode allocation, rmap/refcount, per-AG reservations, transaction/defer, health reporting, buffer operations, and group infrastructure.

## Research Notes

This is the AG lifecycle and geometry authority for XFS. The allocator files depend on its per-AG structures, geometry validation, and AG header initialization. Resize code is the highest-risk area because it mixes AGF/AGI updates, exact allocation/freeing, reservation reinitialization, rmap behavior, and transaction rolling.
