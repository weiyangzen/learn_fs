# File Research: sources/os/linux/linux-stable/fs/xfs/libxfs/xfs_refcount_btree.h

## Scope

Header for refcount btree on-disk block layout accessors, cursor creation, geometry helpers, reserve calculations, staged-tree commits, and cursor cache lifecycle.

## APIs And Macros

- `XFS_REFCOUNT_BLOCK_LEN` defines the short-form CRC btree block header length.
- `XFS_REFCOUNT_REC_ADDR`, `XFS_REFCOUNT_KEY_ADDR`, and `XFS_REFCOUNT_PTR_ADDR` compute record, key, and pointer addresses inside refcount btree blocks.
- Declares `xfs_refcountbt_init_cursor`, `xfs_refcountbt_maxrecs`, `xfs_refcountbt_compute_maxlevels`, `xfs_refcountbt_calc_size`, `xfs_refcountbt_max_size`, `xfs_refcountbt_calc_reserves`, `xfs_refcountbt_commit_staged_btree`, `xfs_refcountbt_maxlevels_ondisk`, and cursor cache lifecycle functions.

## Dependencies

- Forward-declares XFS buffers, btree cursors, mounts, perag structures, transactions, and btree fake-root staging structures.

## Invariants And Risks

- Address macros are part of the userspace-visible libxfs interface and must match the on-disk refcount btree format exactly.
- Pointer layout assumes one key per child pointer, unlike overlapping btrees that carry low and high keys.
