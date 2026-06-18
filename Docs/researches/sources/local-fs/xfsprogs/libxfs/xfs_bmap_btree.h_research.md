# File Research: sources/local-fs/xfsprogs/libxfs/xfs_bmap_btree.h

## Purpose

`xfs_bmap_btree.h` declares the bmap btree interface and defines inline layout helpers for bmap btree records, keys, pointers, inode-root sizing, and btree root reallocation. It is the companion API used by `xfs_bmap.c` and generic btree code to manipulate XFS inode block mapping btrees.

## Main Definitions

- `XFS_BM_MAXLEVELS(mp,w)` returns the computed maximum bmap btree depth for a fork.
- Prototypes cover root conversion, record packing/unpacking, capacity calculation, owner changes, cursor creation, staged-tree commit, btree size calculation, cache lifecycle, and block initialization.

## Record Packing API

The header declares:

- `xfs_bmbt_disk_set_all`
- `xfs_bmbt_disk_get_blockcount`
- `xfs_bmbt_disk_get_startoff`
- `xfs_bmbt_disk_get_all`

These convert between incore extent records and the compact disk record format.

## Capacity API

The header declares and defines helpers for record capacity:

- `xfs_bmbt_get_maxrecs`
- `xfs_bmdr_maxrecs`
- `xfs_bmbt_maxrecs`
- `xfs_bmbt_maxlevels_ondisk`
- `xfs_bmbt_calc_size`

These are used to size bmap btree blocks, inode roots, and cursor caches.

## Layout Helpers

The file provides inline address calculators for incore and ondisk bmap btree layouts:

- `xfs_bmbt_block_len` returns CRC or non-CRC btree block header length.
- `xfs_bmbt_rec_addr` locates records in a btree block.
- `xfs_bmbt_key_addr` locates keys in a btree block.
- `xfs_bmbt_ptr_addr` locates pointers in a btree block.
- `xfs_bmdr_rec_addr` locates records in an inode-root disk layout.
- `xfs_bmdr_key_addr` locates keys in an inode-root disk layout.
- `xfs_bmdr_ptr_addr` locates pointers in an inode-root disk layout.
- `xfs_bmap_broot_ptr_addr` locates pointers in an incore inode root when only root size is known.

The layout model is header first, then records for leaf blocks, or keys followed by pointers for internal/root blocks.

## Root Sizing Helpers

- `xfs_bmap_broot_space_calc` computes incore root bytes for a given record count.
- `xfs_bmap_broot_space` computes incore root space from an ondisk bmdr root.
- `xfs_bmdr_space_calc` computes ondisk inode-root bytes for a record count.
- `xfs_bmap_bmdr_space` computes ondisk space from an incore root.

These helpers are used when converting fork format and checking whether a btree root fits in an inode fork.

## Mutable Root API

`xfs_bmap_broot_realloc` resizes an inode fork's incore bmap btree root to a requested number of records. It is implemented in `xfs_bmap_btree.c` and used by both format conversion and generic btree split/shrink operations.

## Research Notes

This header is mostly structural, but it encodes important disk and memory layout assumptions. Any changes to btree block headers, bmap record size, key size, pointer size, or inode fork sizing must remain consistent with these address and space calculations.
