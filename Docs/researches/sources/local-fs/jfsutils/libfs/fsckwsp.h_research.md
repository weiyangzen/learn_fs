# File Research: sources/local-fs/jfsutils/libfs/fsckwsp.h

## Purpose
Defines the in-memory and in-aggregate workspace model used by JFS fsck: traversal queues, duplicate-block records, inode accounting, block-map workspace pages, service-log state, and the large aggregate-wide fsck control record.

## Major Structures
- Traversal queues: `dtreeQelem` for directory B+ tree nodes and `treeQelem` for non-directory xtree nodes.
- Duplicate allocation tracking: `dupall_blkrec`.
- Workspace block map: `fsck_blk_map_hdr` and `fsck_blk_map_page`.
- Block-map verification workspace: `blkmap_wspace`.
- Inode allocation tracking: `fsck_iag_record`, `fsck_ag_record`, `fsck_iam_record`, `fsck_inode_record`, and extension records.
- Dynamic inode record tables: `inode_tbl_t`, `inode_ext_tbl_t`, `IAG_tbl_t`.
- Workspace extent and reconnect buffers: `wsp_ext_rec`, `recon_buf_record`.
- Main `fsck_agg_record`, which centralizes aggregate geometry, counters, flags, path buffers, traversal queues, duplicate-block lists, inode-table cursors, and all fsck I/O buffers.

## Key Constants
Defines inode type codes, inode extension record kinds, buffer uses, and concrete buffer sizes such as `VLARGE_BUFSIZE`, `FSCKLOG_BUFSIZE`, `BLKMP_IO_BUFSIZE`, `EA_IO_BUFSIZE`, `IAG_IO_BUFSIZE`, and map/node buffer sizes.

## Dependencies
Includes core JFS disk format headers (`jfs_dmap.h`, `jfs_dtree.h`, `jfs_xtree.h`, `jfs_filsys.h`, `jfs_imap.h`, `jfs_dinode.h`) plus `fsck_base.h`, `fscklog.h`, and `fsckcbbl.h`.

## Notes
This header is the central fsck state contract. It contains many raw pointers and bitfields, so it is primarily an in-process workspace definition, with only selected parts intended for stable on-disk interpretation.
