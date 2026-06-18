# File Research: sources/os/linux/linux-stable/fs/freevxfs/vxfs_subr.c

This file provides shared FreeVxFS pagecache and buffer-head helpers for reading file data and metadata.

Major responsibilities:
- Define normal VxFS address-space operations with `read_folio` and `bmap`.
- Read and kmap pages from an address space through `vxfs_get_page()`.
- Release pages through `vxfs_put_page()`.
- Read a logical block of an inode into a buffer head through `vxfs_bread()`.
- Map logical file blocks to physical blocks through `vxfs_getblk()`.
- Implement synchronous folio reads using `block_read_full_folio()`.
- Implement `bmap` using `generic_block_bmap()`.

Important design points:
- `vxfs_getblk()` uses `vxfs_bmap1()` and never allocates blocks; `create` is ignored because the filesystem is read-only.
- A failed block mapping returns `-EIO`.
- `vxfs_bread()` reads physical block zero if `vxfs_bmap1()` fails, so callers must treat failed metadata reads carefully.
- Page checking is stubbed out in comments, indicating no active directory/page validation layer.

Key invariants:
- Pages returned by `vxfs_get_page()` are kmap'ed and must be released with `vxfs_put_page()`.
- Normal file reads always go through block mapping; immediate files use `vxfs_immed_aops` instead.
- No writeback or block allocation operations are provided.

External interfaces:
- Provides `vxfs_aops`, `vxfs_get_page`, `vxfs_put_page`, and `vxfs_bread`.
