# File Research: sources/os/linux/linux/fs/ocfs2/extent_map.h

Public interface for OCFS2 in-memory extent mapping.

Defines:
- `struct ocfs2_extent_map_item`: cached logical cluster start, physical cluster start, cluster count, flags, and list link.
- `OCFS2_MAX_EXTENT_MAP_ITEMS`: small fixed cache size of 3 entries.
- `struct ocfs2_extent_map`: count plus list head.

Exports:
- Cache lifecycle and mutation: `ocfs2_extent_map_init()`, `ocfs2_extent_map_trunc()`, `ocfs2_extent_map_insert_rec()`.
- File mapping: `ocfs2_get_clusters()`, `ocfs2_extent_map_get_blocks()`.
- Fiemap: `ocfs2_fiemap()`.
- Overwrite and seek helpers: `ocfs2_overwrite_io()`, `ocfs2_seek_data_hole_offset()`.
- Xattr extent mapping: `ocfs2_xattr_get_clusters()`.
- Virtual block read helpers: `ocfs2_read_virt_blocks()` and single-block wrapper `ocfs2_read_virt_block()`.
- Hole sizing helper: `ocfs2_figure_hole_clusters()`.

Contract:
- `ocfs2_read_virt_block()` validates non-NULL output buffer pointer and delegates to the multi-block form.
- Allocation-stable callers should hold the inode allocation semaphore as documented by the implementation.
