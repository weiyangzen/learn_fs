# File Research: sources/os/linux/linux/fs/freevxfs/vxfs_subr.c

Read status: complete, 152 lines.

Purpose: shared FreeVxFS page-cache, buffer, and block-mapping helpers.

Key flow:
- `vxfs_aops` supplies normal `.read_folio` and `.bmap`.
- `vxfs_get_page()` reads a mapping page via `read_mapping_page()` and kmaps it.
- `vxfs_put_page()` kunmaps and drops a page.
- `vxfs_bread()` maps a logical inode block through `vxfs_bmap1()` and reads the physical block via `sb_bread()`.
- `vxfs_getblk()` maps buffer heads for block reads; returns `-EIO` when mapping is zero.
- `vxfs_read_folio()` delegates to `block_read_full_folio()`.
- `vxfs_bmap()` delegates to `generic_block_bmap()`.

Important dependencies: `vxfs_bmap1`, buffer-head block helpers, page cache read helpers.

Risk note: this is read-only support; block creation is ignored even though the get_block signature includes `create`.
