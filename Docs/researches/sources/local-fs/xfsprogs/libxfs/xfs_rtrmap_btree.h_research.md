# File Research: sources/local-fs/xfsprogs/libxfs/xfs_rtrmap_btree.h

This header exposes the realtime rmap btree interface and packed layout helpers for in-memory and on-disk inode roots.

`XFS_RTRMAP_BLOCK_LEN` is the CRC long-btree header length. The exported API includes disk cursor/stage/commit helpers, max record and maxlevel calculations, cursor cache lifecycle, reserve sizing, inode-format load/flush, conversion to disk, metadata inode creation, realtime-superblock rmap initialization, in-memory btree cursor/init helpers, and `xfs_rtrmap_highest_rgbno`.

The record/key/pointer address helpers reflect overlapping-rmap layout. A leaf root uses `struct xfs_rmap_rec` records. An internal root stores low and high keys as two adjacent `struct xfs_rmap_key` entries per record, followed by `xfs_rtrmap_ptr_t` pointers. The same distinction exists for the on-disk `struct xfs_rtrmap_root` format.

`xfs_rtrmap_broot_space_calc` and `xfs_rtrmap_droot_space_calc` calculate in-memory and on-disk root sizes. These functions are required by the reallocation and verifier paths to avoid writing a root that exceeds the inode fork. The header also forward-declares `struct xfbtree`, tying this file to optional in-memory btree support.
