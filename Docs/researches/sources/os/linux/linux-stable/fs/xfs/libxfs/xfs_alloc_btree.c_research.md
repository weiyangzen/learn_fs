# File Research: sources/os/linux/linux-stable/fs/xfs/libxfs/xfs_alloc_btree.c

## Purpose

This file implements the XFS free-space btree operations for the by-block-number tree (BNOBT) and by-count tree (CNTBT), including cursor construction, block allocation/free callbacks, key comparisons, verifiers, staged btree commit, and cursor cache lifecycle.

## Main Responsibilities

- Provide `xfs_btree_ops` for BNOBT and CNTBT.
- Allocate and free free-space btree blocks via the AGFL.
- Maintain AGF root pointers and btree levels.
- Verify free-space btree blocks on read/write.
- Define record/key ordering semantics for both trees.
- Construct cursors for normal and staged btree use.
- Calculate max records, max on-disk levels, and btree size.
- Manage the allocator btree cursor slab cache.

## BNOBT Versus CNTBT Semantics

- BNOBT:
  - Ordered by `ar_startblock`.
  - High key is the end block of the extent.
  - Records are in order if previous start plus length is less than or equal to next start.
  - Supports contiguous key checks.
- CNTBT:
  - Ordered by `ar_blockcount`, then `ar_startblock`.
  - High key is the block count.
  - Used to find largest/best-fit free extents.

## Key Functions

- Cursor duplication:
  - `xfs_bnobt_dup_cursor`
  - `xfs_cntbt_dup_cursor`
- Root/counter updates:
  - `xfs_allocbt_set_root`
- Block allocation/free:
  - `xfs_allocbt_alloc_block`
  - `xfs_allocbt_free_block`
- Key/record handling:
  - init key from record
  - init high key from record
  - init record from cursor
  - init root pointer from AGF
  - compare key with cursor
  - compare two keys
  - key/record order checks
- Verifiers:
  - `xfs_allocbt_verify`
  - read/write verify callbacks
  - `xfs_bnobt_buf_ops`
  - `xfs_cntbt_buf_ops`
- Cursor constructors:
  - `xfs_bnobt_init_cursor`
  - `xfs_cntbt_init_cursor`
- Repair/staging support:
  - `xfs_allocbt_commit_staged_btree`
- Geometry:
  - `xfs_allocbt_maxrecs`
  - `xfs_allocbt_maxlevels_ondisk`
  - `xfs_allocbt_calc_size`
- Cache lifecycle:
  - `xfs_allocbt_init_cur_cache`
  - `xfs_allocbt_destroy_cur_cache`

## Important Invariants and Edge Cases

- New btree blocks are allocated from AGFL. If no block is available, allocation callback returns `stat = 0`.
- Freed btree blocks are put back on AGFL and inserted into the busy extent list with discard skipped.
- Global `m_allocbt_blks` is incremented/decremented for allocation btree blocks.
- Verifier uses per-AG cached btree levels when AGF is initialized; otherwise it falls back to mount maximum levels for grow/recovery contexts.
- Online repair can temporarily validate against alternate repair btree heights.
- Cursor constructors hold a group reference and set cursor levels from AGF if an AGF buffer is provided.
- Staged btree commit installs fake-root state into AGF and logs root/level fields.

## Dependencies

- Generic XFS btree framework.
- AGFL allocation helpers from `xfs_alloc.c`.
- Per-AG state from `xfs_ag.h`.
- Busy extent tracking.
- Health marking through btree sick masks.
- Online repair staging support.

## Research Notes

This file supplies the polymorphic btree behavior that `xfs_alloc.c` relies on. The allocator’s dual-tree consistency depends on these ordering rules, verifier limits, AGF root updates, and AGFL-backed btree block allocation/free callbacks.
