# File Research: sources/os/linux/linux-stable/fs/xfs/libxfs/xfs_bmap_btree.h

## Purpose

`xfs_bmap_btree.h` declares the bmap btree interface and inline layout helpers. It is the shared contract between the high-level bmap implementation, inode fork code, and the bmap btree backend.

## Public Btree Interfaces

The header declares:

- Root conversion: `xfs_bmdr_to_bmbt`, `xfs_bmbt_to_bmdr`.
- Packed record conversion: `xfs_bmbt_disk_set_all`, `xfs_bmbt_disk_get_all`, `xfs_bmbt_disk_get_blockcount`, `xfs_bmbt_disk_get_startoff`.
- Capacity helpers: `xfs_bmbt_get_maxrecs`, `xfs_bmdr_maxrecs`, `xfs_bmbt_maxrecs`, `xfs_bmbt_maxlevels_ondisk`, `xfs_bmbt_calc_size`.
- Cursor and staged tree operations: `xfs_bmbt_init_cursor`, `xfs_bmbt_commit_staged_btree`.
- Owner changes: `xfs_bmbt_change_owner`.
- Cache lifecycle: `xfs_bmbt_init_cur_cache`, `xfs_bmbt_destroy_cur_cache`.
- Block initialization: `xfs_bmbt_init_block`.
- In-core root resizing: `xfs_bmap_broot_realloc`.

`XFS_BM_MAXLEVELS(mp, w)` reads per-mount computed bmap btree max level for a fork.

## Layout Helpers

The inline helpers compute addresses inside three related layouts:

- In-core bmap btree blocks via `xfs_bmbt_rec_addr`, `xfs_bmbt_key_addr`, and `xfs_bmbt_ptr_addr`.
- On-disk dinode btree root blocks via `xfs_bmdr_rec_addr`, `xfs_bmdr_key_addr`, and `xfs_bmdr_ptr_addr`.
- In-core inode btree roots via `xfs_bmap_broot_ptr_addr`.

Space calculation helpers include:

- `xfs_bmbt_block_len`, which selects CRC or non-CRC btree block header size.
- `xfs_bmap_broot_space_calc`, for in-core root size from a record count.
- `xfs_bmap_broot_space`, for in-core root size from an on-disk root.
- `xfs_bmdr_space_calc`, for on-disk dinode-root size.
- `xfs_bmap_bmdr_space`, for on-disk root size from an in-core root block.

## Important Invariants

- Bmap btree roots store keys and pointers, not leaf records, when the root level is above zero.
- In-core and on-disk root layouts differ, so callers must use the correct accessor family.
- Pointer arrays are positioned after the maximum key array for the current block/root capacity.
- Header size depends on CRC support, so raw pointer arithmetic must go through these helpers.

## Dependencies and Consumers

The header is consumed directly by `xfs_bmap.c`, `xfs_bmap_btree.c`, and any XFS code that needs to inspect or manipulate bmap btree roots. It depends on on-disk bmap record and root structures from XFS format headers and generic btree cursor/block declarations.

## Research Notes

This header is small but layout-sensitive. Changes to address calculations, space calculations, or max-record declarations can silently corrupt inode-root btrees or mis-copy root keys and pointers during fork conversion.
