# File Research: sources/os/linux/linux-stable/fs/netfs/write_issue.c

Issues high-level netfs writeback, writethrough, cache-copy, and single-object writes.

Key behavior:
- Creates write requests with upload stream 0 and cache stream 1.
- Begins FS-Cache write operation when cacheable and cache is enabled.
- `netfs_write_folio()` handles writeback of dirty folios, partial streaming writes, EOF zeroing, dirty groups, copy-to-cache-only folios, and discontinuities.
- Builds subrequests incrementally with `netfs_advance_write()`, splitting by max write size, max segments, discontiguity, or EOF.
- `netfs_writepages()` serializes on `ictx->wb_lock`, iterates VFS writeback folios, starts upload when first non-copy-to-cache folio appears, and offloads collection.
- Writethrough path holds writeback lock across pagecache population, then writes folios as page ends are reached.
- Single-object writeback writes an `ITER_FOLIOQ` payload, used for monolithic objects.
- On unrecoverable startup failure, dirty pages are killed by starting/ending writeback and dropping netfs private metadata.

Important design:
- Upload and cache writes are overlaid over the same rolling folio buffer but can produce different subrequest boundaries.
