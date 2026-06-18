# File Research: sources/os/linux/linux/fs/gfs2/aops.c

Implements GFS2 address-space operations for normal and journaled-data files, including read, writeback, readahead, bmap, dirtying, invalidation, and folio release.

Key entry points:
- `gfs2_jdata_writeback()`
- `gfs2_internal_read()`
- `adjust_fs_space()`
- `gfs2_release_folio()`
- `gfs2_set_aops()`

Important control flow:
- Normal writeback uses `iomap_writepages()` with `gfs2_writeback_ops`; if no pages were written, it forces AIL flush to avoid dirty throttling loops.
- Journaled-data writeback uses custom batching so GFS2 can begin transactions before locking folios.
- `gfs2_read_folio()` chooses iomap read for non-jdata, stuffed read for inline data, or `mpage_read_folio()` for journaled data with buffers.
- `stuffed_read_folio()` reads inline file data from the dinode and zero-fills the folio tail.
- `adjust_fs_space()` updates statfs accounting after filesystem grow by comparing rindex total space with master/local statfs state.
- `gfs2_invalidate_folio()` and `gfs2_release_folio()` handle buffer-head/journal metadata cleanup for jdata mappings.

Dependencies and integration:
- Uses iomap, mpage, buffer heads, GFS2 transactions, log/AIl, quota/statfs, glocks, and bmap mapping.
- `gfs2_set_aops()` selects `gfs2_jdata_aops` for journaled-data inodes and `gfs2_aops` otherwise.

Risks and invariants:
- Journaled writeback asserts the inode glock is exclusive.
- Jdata dirtying marks folios checked when inside a transaction.
- Release refuses folios with active buffer refs, transaction-owned bufdata, dirty buffers, or pinned buffers.
