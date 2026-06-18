# File Research: sources/os/linux/linux/fs/iomap/buffered-io.c

Buffered I/O implementation for iomap users. It handles folio state tracking, buffered reads/readahead, buffered writes, inline data, delayed-allocation cleanup, zeroing, page-mkwrite, and writeback.

Folio state:
- `struct iomap_folio_state` tracks per-block uptodate and dirty bits plus pending read/write byte counts.
- Helpers allocate/free state only when block size is smaller than folio size or partial tracking is needed.
- Range helpers set/clear/find uptodate and dirty block ranges.

Read path:
- `iomap_read_folio()` and `iomap_readahead()` drive `iomap_iter()` and submit ranges through `iomap_read_ops`.
- Handles holes, newly allocated blocks, post-EOF zeroing, inline data, fsverity metadata/zerohash synthesis, and partially uptodate folios.
- `iomap_finish_folio_read()` completes sub-folio reads and reports buffered read errors.

Write path:
- `iomap_file_buffered_write()` iterates mappings and writes user data through `iomap_write_iter()`.
- `iomap_write_begin()` obtains a folio, validates stale mappings, prepares needed blocks through zeroing or reads, and supports buffer-head fallback.
- `iomap_write_end()` marks copied ranges uptodate/dirty or updates inline data.
- Short writes revert iter state, shrink chunk size for large folios, and truncate newly allocated pagecache beyond EOF.

Delayed allocation and unshare:
- `iomap_write_delalloc_release()` scans dirty pagecache to punch only unused delalloc reservations after short writes.
- `iomap_file_unshare()` forces shared extents into private dirty pagecache via `IOMAP_UNSHARE`.

Zeroing and mmap:
- `iomap_zero_range()` and `iomap_truncate_page()` zero pagecache ranges, batching dirty folios where useful and flushing stale unwritten mappings.
- `iomap_page_mkwrite()` prepares a mapped folio for write faults and returns it locked on success.

Writeback:
- `iomap_writeback_folio()` handles EOF truncation/zeroing, starts writeback, finds dirty ranges, invokes filesystem `writeback_range`, clears dirty tracking, reports errors, and completes writeback accounting.
- `iomap_writepages()` iterates dirty folios and submits filesystem writeback, refusing reclaim-context writeback except as a warning/error path.

Risks and invariants:
- Folio private state pending counters must reach zero before free.
- Stale iomap detection prevents data corruption when extent state changes under buffered writes.
- Delalloc release requires `invalidate_lock` held write-side to avoid page-fault races.
- EOF handling avoids writing post-EOF data except fsverity metadata.
- Large-folio, sub-block dirty tracking, fsverity, buffer-head fallback, and block-device BIO helpers all share this path, so changes have broad filesystem impact.
