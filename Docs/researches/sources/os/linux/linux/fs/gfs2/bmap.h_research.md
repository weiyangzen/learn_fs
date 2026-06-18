# File Research: sources/os/linux/linux/fs/gfs2/bmap.h

Declares GFS2 block mapping, iomap, allocation, truncation, journal extent, and hole-punch interfaces.

Key exports:
- `gfs2_write_calc_reserv()` estimates data and indirect blocks needed for a write.
- `gfs2_iomap_ops`, `gfs2_iomap_write_ops`, `gfs2_writeback_ops`
- `gfs2_unstuff_dinode()`, `gfs2_block_map()`, `gfs2_iomap_get()`, `gfs2_iomap_alloc()`
- `gfs2_get_extent()`, `gfs2_alloc_extent()`
- `gfs2_setattr_size()`, `gfs2_truncatei_resume()`, `gfs2_file_dealloc()`
- `gfs2_map_journal_extents()`, `gfs2_free_journal_extents()`
- `gfs2_write_alloc_required()`
- `__gfs2_punch_hole()`

Integration:
- Shared by address-space, file, directory, inode, journal, and recovery paths.
