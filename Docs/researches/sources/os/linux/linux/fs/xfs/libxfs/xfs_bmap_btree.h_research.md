# File Research: sources/os/linux/linux/fs/xfs/libxfs/xfs_bmap_btree.h

## Purpose

`xfs_bmap_btree.h` declares the bmap btree interface and inline layout helpers. It is the shared contract between the high-level block mapping code, inode fork code, and the bmap btree backend.

## Public Interfaces

The header declares:

- maximum bmap btree level access through `XFS_BM_MAXLEVELS`
- dinode-root to btree-root conversion
- packed bmap record get/set helpers
- btree-root to dinode-root conversion
- max-record and sizing helpers
- bmap btree owner changes
- cursor initialization
- staged btree commit
- cursor cache lifecycle
- btree block initialization
- in-core root reallocation

## Layout Helpers

Inline helpers compute addresses for:

- in-core bmap btree records, keys, and pointers
- on-disk dinode root records, keys, and pointers
- in-core inode btree root pointers
- CRC-aware btree block header length
- in-core btree root space
- on-disk dinode root space

Important helpers include:

- `xfs_bmbt_block_len`
- `xfs_bmbt_rec_addr`
- `xfs_bmbt_key_addr`
- `xfs_bmbt_ptr_addr`
- `xfs_bmdr_rec_addr`
- `xfs_bmdr_key_addr`
- `xfs_bmdr_ptr_addr`
- `xfs_bmap_broot_ptr_addr`
- `xfs_bmap_broot_space_calc`
- `xfs_bmdr_space_calc`

## Notable Invariants

- In-core btree blocks and on-disk dinode roots have different layouts.
- Header size depends on CRC support.
- Pointer arrays are positioned after the maximum key array for the chosen capacity.
- Root-space calculations must match inode fork sizing constraints.
- Callers must use the correct accessor family for the representation they are manipulating.

## Research Notes

This header is small but layout-sensitive. Any mistake in address calculation, header-size selection, root-space calculation, or max-record usage can corrupt inode-root bmap btrees during fork conversion, root growth/shrink, or btree staging.
