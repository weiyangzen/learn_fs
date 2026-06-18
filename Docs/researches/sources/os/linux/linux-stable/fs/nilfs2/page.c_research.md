# File Research: sources/os/linux/linux-stable/fs/nilfs2/page.c

`page.c` implements NILFS-specific folio and buffer-head handling. It provides buffer grabbing, state copying, dirty clearing, shadow-cache page copying, and discovery of delayed/uncommitted extents.

`nilfs_grab_buffer()` grabs or creates the folio for a block offset, creates buffers as needed, waits on the selected buffer, sets its block device, and returns the buffer. `nilfs_forget_buffer()` clears uptodate/dirty/mapped/async/write/delay/NILFS-specific state bits, resets the block number, clears folio uptodate/mapped state, and drops the buffer reference. `nilfs_copy_buffer()` copies data and inherent buffer state while updating destination folio uptodate/mapped state based on all buffers in the folio.

For shadow metadata handling, `nilfs_copy_dirty_pages()` copies dirty tagged folios from one mapping to another, preserving dirty buffer states; `nilfs_copy_back_pages()` copies or moves folios from a shadow mapping back into the original mapping without adding pages during the process. These functions are used by metadata shadow-map code in `mdt.c`.

Dirty-state cleanup is deliberately careful. `nilfs_clear_dirty_pages()` iterates dirty tagged folios and calls `nilfs_clear_folio_dirty()` only if the folio still belongs to the mapping. `nilfs_clear_folio_dirty()` refuses to clear busy/locked buffer sets until after invalidating bh LRUs, clears NILFS buffer state bits, resets folio state, and calls `__nilfs_clear_folio_dirty()`, which updates xarray dirty tags under the mapping lock before clearing dirty-for-IO.

`nilfs_find_uncommitted_extent()` scans contiguous cached folios for buffers marked delayed, returning the first extent length and start block. This is used by inode/writeback logic to reason about uncommitted delayed allocation ranges.
