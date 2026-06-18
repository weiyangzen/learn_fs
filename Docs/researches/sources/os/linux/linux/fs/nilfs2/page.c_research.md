# File Research: sources/os/linux/linux/fs/nilfs2/page.c

`page.c` implements NILFS-specific folio and buffer-head handling. It manages buffer states beyond the generic buffer flags, copies buffers between normal and shadow mappings, clears dirty state safely, and locates delayed/uncommitted extents.

`nilfs_grab_buffer()` grabs or creates the folio containing a logical block offset, returns the requested buffer head, waits on it, and assigns the filesystem block device. `nilfs_forget_buffer()` clears mapping/dirty/uptodate/delay/NILFS-specific state, resets `b_blocknr`, updates folio state, and releases the buffer.

`nilfs_copy_buffer()` and the internal `nilfs_copy_folio()` copy data and selected buffer flags while preserving page-level uptodate/mappedtodisk consistency. `nilfs_copy_dirty_pages()` copies dirty folios from one address space to another, preserving dirty buffers; `nilfs_copy_back_pages()` copies or moves shadow-cache folios back into the original mapping.

Dirty cleanup is careful around buffer references. `nilfs_clear_folio_dirty()` clears a folio only after confirming buffers are not busy, retrying after invalidating buffer-head LRU state. `__nilfs_clear_folio_dirty()` directly updates the xarray dirty tag and folio dirty state, supporting cases where NILFS must cancel dirty accounting outside ordinary writeback.

`nilfs_find_uncommitted_extent()` scans contiguous cached folios for `BH_Delay` buffers and returns the first delayed extent length and block offset. This is used to find data not yet committed into a NILFS log.
