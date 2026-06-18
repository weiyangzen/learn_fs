# File Research: sources/os/linux/linux/fs/hpfs/buffer.c

Purpose: Provides HPFS buffer mapping helpers for single sectors and 4-sector structures, including hotfix remapping and readahead.

Key functions:
- `hpfs_search_hotfix_map()` maps bad original sectors to spare replacement sectors.
- `hpfs_search_hotfix_map_for_range()` shortens contiguous ranges at hotfix boundaries.
- `hpfs_prefetch_sectors()` issues readahead when sectors are valid and not hotfixed.
- `hpfs_map_sector()` reads a sector buffer after hotfix translation.
- `hpfs_get_sector()` obtains a sector buffer for writing without reading existing data.
- `hpfs_map_4sectors()` maps a 4-sector block, allocating a contiguous 2048-byte bounce buffer if buffer_head data is not contiguous.
- `hpfs_get_4sectors()` obtains a 4-sector writable block without reading.
- `hpfs_brelse4()` releases 4-sector mappings and frees bounce buffers.
- `hpfs_mark_4buffers_dirty()` copies bounce-buffer data back and marks all four buffers dirty.

Dependencies and integration:
- All HPFS on-disk structure access flows through these helpers.
- Requires the global HPFS mutex, asserted in mapping paths.

Risk notes:
- Dnodes and bitmaps are 4-sector structures; unaligned 4-sector mapping is rejected.
- Bounce-buffer handling is essential when buffer_head memory is not physically adjacent in kernel virtual memory.
