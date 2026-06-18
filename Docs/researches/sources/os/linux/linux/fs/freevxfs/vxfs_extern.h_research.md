# File Research: sources/os/linux/linux/fs/freevxfs/vxfs_extern.h

Read status: complete, 49 lines.

Purpose: declares cross-file FreeVxFS symbols.

Exports declared:
- Block mapping: `vxfs_bmap1`.
- Fileset setup: `vxfs_read_fshead`.
- Inode operations: `vxfs_blkiget`, `vxfs_stiget`, `vxfs_iget`, `vxfs_evict_inode`, diagnostic `vxfs_dumpi` when built.
- Directory ops: `vxfs_dir_inode_ops`, `vxfs_dir_operations`.
- OLT setup: `vxfs_read_olt`.
- Page/block helpers: `vxfs_aops`, `vxfs_get_page`, `vxfs_put_page`, `vxfs_bread`.

Integration note: this header is the local module boundary tying the FreeVxFS object files together.
