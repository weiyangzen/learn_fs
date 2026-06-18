# File Research: sources/os/linux/linux/fs/gfs2/meta_io.c

Implements metadata address-space writeback, metadata buffer lookup/read helpers, metadata readahead, and journal wipe support for freed or deleted blocks.

Key exported functions include `gfs2_meta_new`, `gfs2_meta_read`, `gfs2_meta_wait`, `gfs2_getbuf`, `gfs2_journal_wipe`, `gfs2_meta_buffer`, and `gfs2_meta_ra`.

Important behavior:
- Defines `gfs2_meta_aops` and `gfs2_rgrp_aops`, both using buffer-backed dirty/invalidate/writepages/release/migrate operations.
- `gfs2_aspace_write_folio()` locks dirty mapped buffers, marks them for async write with `set_buffer_async_write()`, submits writes with `bh_submit()` and `bh_end_async_write`, starts/ends folio writeback, and redirties on nonblocking lock failure.
- `gfs2_getbuf()` maps a filesystem block into either a glock-specific address space or the global metadata address space, creating buffers when requested.
- `gfs2_meta_new()` prepares a new metadata buffer with uptodate state and `GFS2_MAGIC`.
- `gfs2_meta_read()` can issue the requested read plus one-block readahead, batching consecutive buffer heads into bios through `gfs2_submit_bhs()`, and waits when `DIO_WAIT` is set.
- `gfs2_meta_read_endio()` walks bio folios and completes each involved buffer via `end_buffer_read_sync()`.
- `gfs2_meta_wait()` validates read completion and reports I/O errors, including transaction-touched buffer diagnostics.
- `gfs2_journal_wipe()` removes freed ranges from AIL/journal state and clears metadata or jdata buffers from the journal.
- `gfs2_meta_buffer()` reads and validates a specific metadata type; `gfs2_meta_ra()` performs extent readahead with the tuned maximum.

This file is the common buffer-cache substrate for GFS2 metadata. Risk areas include buffer lifetime/refcounts, dirty/pinned journal interactions during block deletion, and avoiding stale metadata after withdraw.
