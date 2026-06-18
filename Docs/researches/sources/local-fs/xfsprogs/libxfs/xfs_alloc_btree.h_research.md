# File Research: sources/local-fs/xfsprogs/libxfs/xfs_alloc_btree.h

## Purpose

`xfs_alloc_btree.h` declares on-disk layout access macros and public helpers for XFS allocation free-space btrees. It is the interface between allocation code, repair/staging code, and the generic btree implementation.

## Layout Macros

- `XFS_ALLOC_BLOCK_LEN(mp)` returns the short btree block header size, selecting CRC or non-CRC header length.
- `XFS_ALLOC_REC_ADDR(mp, block, index)` computes the 1-based record address in a btree block.
- `XFS_ALLOC_KEY_ADDR(mp, block, index)` computes the key address.
- `XFS_ALLOC_PTR_ADDR(mp, block, index, maxrecs)` computes the pointer address after the key array.

The comment notes that some macros appear unused in-kernel but are used in userspace, which matters for xfsprogs/libxfs compatibility.

## Cursor Constructors and Sizing APIs

- `xfs_bnobt_init_cursor`
- `xfs_cntbt_init_cursor`
- `xfs_allocbt_maxrecs`
- `xfs_allocbt_calc_size`
- `xfs_allocbt_maxlevels_ondisk`

These construct bno/count btree cursors and compute btree record capacity, size, and maximum height.

## Staging and Cache Lifecycle

- `xfs_allocbt_commit_staged_btree` installs a staged allocation btree root into AGF.
- `xfs_allocbt_init_cur_cache` and `xfs_allocbt_destroy_cur_cache` manage cursor cache allocation.

## Integration Notes

This header is included by `xfs_alloc.c`, `xfs_alloc_btree.c`, repair code, and any code that needs to inspect or rebuild free-space btree blocks. It forward-declares `xbtree_afakeroot`, reflecting online/offline repair staging support.
