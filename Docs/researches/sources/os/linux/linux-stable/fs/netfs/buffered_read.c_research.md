# File Research: sources/os/linux/linux-stable/fs/netfs/buffered_read.c

## Purpose

`buffered_read.c` implements high-level buffered read helpers for network filesystems using the Linux page cache. It supports readahead, read-folio, read-for-write prefetch, partial dirty folio gap filling, cache-backed reads through FS-Cache, server reads, and zero-fill beyond the netfs zero point/EOF.

The exported helpers are intended for filesystems that embed `struct netfs_inode` adjacent to their inode and provide netfs operations.

## Main Entry Points

- `netfs_readahead(struct readahead_control *ractl)`
  - Handles VM readahead into pagecache.
  - May expand the request based on cache and filesystem preferences.
  - Reads from cache, server, or zero-fill sources.

- `netfs_read_folio(struct file *file, struct folio *folio)`
  - Handles a single folio read.
  - If folio is dirty due to streaming write state, delegates to `netfs_read_gaps()`.

- `netfs_write_begin(...)`
  - Deprecated helper for old write-begin paths.
  - Preloads a folio before partial write if necessary.

- `netfs_prefetch_for_write(struct file *file, struct folio *folio, size_t offset, size_t len)`
  - Reads folio contents before a write that requires existing data.

- `netfs_buffered_read_iter(struct kiocb *iocb, struct iov_iter *iter)`
  - Buffered `read_iter()` helper.
  - Uses `filemap_read()` inside netfs read serialization.

- `netfs_file_read_iter(struct kiocb *iocb, struct iov_iter *iter)`
  - Generic netfs read dispatcher.
  - Uses unbuffered/direct path when `IOCB_DIRECT` or `NETFS_ICTX_UNBUFFERED` is set; otherwise buffered read.

## Request Expansion

`netfs_rreq_expand()` gives both local cache and filesystem a chance to widen readahead:

- `netfs_cache_expand_readahead()` calls cache `expand_readahead()` if present.
- Filesystem `rreq->netfs_ops->expand_readahead()` may also adjust.
- `readahead_expand()` reconciles VM readahead state with the requested range.

This lets cache granularity, RPC sizes, and THP-friendly boundaries influence read size while still containing the original requested region.

## Cache Operation Setup

`netfs_begin_cache_read()` calls `fscache_begin_read_operation()` with the inode cookie. Failures such as `-ENOMEM`, `-EINTR`, or `-ERESTARTSYS` cause request cleanup.

Cache read source selection:

- `netfs_cache_prepare_read()` asks cache ops to prepare a read.
- If no cache ops exist, default source is `NETFS_DOWNLOAD_FROM_SERVER`.
- Cache may return `NETFS_READ_FROM_CACHE` or another source state.

## Subrequest Preparation And Dispatch

`netfs_read_to_pagecache()` is the main slicer:

1. Allocates `netfs_io_subrequest`.
2. Queues it on the request stream with `netfs_queue_read()`.
3. Chooses cache/server/zero-fill source.
4. Applies zero-point and EOF handling.
5. Calls filesystem `prepare_read()` for server reads.
6. Prepares the iterator with `netfs_prepare_read_iterator()`.
7. Marks `NETFS_RREQ_ALL_QUEUED` when all slices are queued.
8. Dispatches through `netfs_issue_read()`.

`netfs_prepare_read_iterator()`:

- Limits server reads to stream `sreq_max_len`.
- Loads folios from `readahead_control` into the rolling buffer as needed.
- Applies segment limits using `netfs_limit_iter()`.
- Assigns `subreq->io_iter`, truncates it, and advances the rolling buffer.

`netfs_issue_read()` dispatches by source:

- Server: `rreq->netfs_ops->issue_read(subreq)`.
- Cache: `netfs_read_cache_to_pagecache()`.
- Zero-fill/default: zeros iterator, marks transferred, completes subrequest.

## Rolling Buffer Use

Readahead and folio reads use `rolling_buffer`:

- `rolling_buffer_init()` creates request buffer state.
- `rolling_buffer_load_from_ra()` extracts folios from VM readahead.
- `rolling_buffer_append()` creates singular buffers for one folio.
- `rolling_buffer_advance()` advances after slicing.

This abstracts pagecache folios as I/O iterators for server/cache operations.

## Dirty Folio Gap Reads

`netfs_read_gaps()` handles a folio that is dirty but only partially populated due to streaming writes:

- Reads only gaps before/after the dirty range into the real folio.
- Routes the already-dirty middle range into a temporary sink folio.
- Builds a bvec iterator combining real folio and sink.
- On success, clears netfs folio info, restores group/private state, flushes dcache, marks folio uptodate.

This avoids overwriting locally dirty data while still completing folio contents.

## Write-Begin And Prefetch Paths

`netfs_skip_folio_read()` decides if a write can avoid pre-reading:

- Full folio write.
- Folio entirely beyond EOF.
- Write from folio start through EOF.
- Optional `always_fill` mode for complete zeroing beyond EOF.

`netfs_write_begin()`:

- Gets/locks folio.
- Lets filesystem `check_write_begin()` resolve conflicts.
- Skips read when safe.
- Otherwise allocates read-for-write request and reads the folio.

`netfs_prefetch_for_write()` is a focused prefetch helper for modern write paths.

## Synchronization And Error Handling

- Request completion waits are performed with `netfs_wait_for_read()`.
- Readahead sets `NETFS_RREQ_OFFLOAD_COLLECTION` for async collection.
- Subrequest list insertion uses spinlock plus release ordering.
- `NETFS_RREQ_ALL_QUEUED` is published with write barriers before waking collectors.
- Folios are unlocked on completion or cleanup paths.
- Errors are stored with `cmpxchg(&rreq->error, 0, ret)` so earlier errors are preserved.

## Exports

Exports:

- `netfs_readahead`
- `netfs_read_folio`
- `netfs_write_begin`
- `netfs_buffered_read_iter`
- `netfs_file_read_iter`

## Key Takeaways

This file is the buffered-read orchestration layer for netfs. It turns VM read and readahead requests into source-aware netfs subrequests, safely mixing local cache reads, server downloads, and zero-fill while preserving pagecache and dirty-folio correctness.
