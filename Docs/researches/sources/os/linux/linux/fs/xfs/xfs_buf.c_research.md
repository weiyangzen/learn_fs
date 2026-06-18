# File Research: sources/os/linux/linux/fs/xfs/xfs_buf.c

Implements the XFS metadata buffer cache: allocation, lookup, backing memory, I/O submission, verification, lifecycle, LRU shrinking, delayed write queues, and buffer target setup.

Key elements:
- `xfs_buf_stale` marks a locked buffer stale, clears delwri state, removes it from LRU, and prevents stale buildup.
- Backing memory allocation supports xmbuf/tmpfs mapping for memory targets, aligned kmalloc for sub-page power-of-two buffers, single folio/high-order folio buffers, and vmalloc fallback.
- `xfs_buf_alloc` initializes buffer state, maps, lock/refcount, LRU ref, pin waiters, target/mount, and backing memory.
- Buffer lookup uses an rhashtable keyed by starting daddr and total length; stale length mismatches are tolerated for busy reallocation cases.
- `xfs_buf_get_map` verifies range/sector alignment, takes per-AG references, looks up or inserts a buffer, handles incore-only lookup, clears stale errors for non-read callers, and returns a locked buffer.
- `xfs_buf_read_map` reads and verifies buffers, re-verifies cached buffers missing ops, marks failed reads stale, maps bad CRC to `-EFSCORRUPTED`, and reports metadata I/O errors.
- `xfs_buf_readahead_map` performs trylock async read-ahead except for memory targets.
- Uncached buffer helpers allocate buffers outside the hash by using `XFS_BUF_DADDR_NULL`.
- Reference lifecycle uses `lockref`, rhashtable removal, LRU insertion, RCU freeing, per-AG ref release, and immediate destruction for uncached or non-LRU buffers.
- Buffer locking uses a semaphore; stale pinned buffers force the log before blocking.
- I/O completion verifies reads, verifies writes before submission, handles vmalloc cache invalidation, updates `XBF_DONE`, processes buffer log items, calls optional iodone, and releases async refs.
- Async write error handling retries transient metadata write errors, marks log items failed for retry, escalates permanent failures to filesystem shutdown, and stales failed buffers.
- Bio submission builds one bio over contiguous virtual memory and splits/chains bios for compound buffer maps.
- Buftarg lifecycle initializes hash/LRU/shrinker/readahead counters, configures sector sizes and atomic write unit geometry, opens DAX holders, syncs blockdev pagecache, drains outstanding buffers, and frees targets.
- Delayed write helpers queue, cancel, synchronously submit, or nowait-submit sorted buffer lists; stale/synchronously written buffers are lazily removed from delwri lists.
- `xfs_verify_magic` and `xfs_verify_magic16` compare on-disk magic values against buffer verifier tables.

Dependencies:
- Uses Linux rhashtable, list_lru, shrinker, lockref, bio, folio/vmalloc, blockdev, DAX, and workqueue APIs.
- Integrates with XFS log, transaction buffer items, error injection/configuration, per-AG lifetime, and in-memory buffer target code.

Research notes:
- Lock ordering is documented for stale, release, buftarg drain, and shrinker isolation paths.
- New cached buffers are locked and held before insertion so RCU lookups racing insertion cannot use unlocked uninitialized buffers.
- Read errors clear `XBF_DONE` and stale the buffer so future cache lookups reread from disk.
- Write verification failure forces shutdown with `SHUTDOWN_CORRUPT_INCORE`.
- Async I/O completion is punted to `m_buf_workqueue` to process buffer/log-item completion outside bio completion context.
- Delwri nowait submission intentionally skips locked or pinned buffers and leaves them on the caller’s list for later retry/cancel.
- Draining a buftarg warns if buffers with permanent write failure are freed, because dirty metadata was discarded after shutdown.
