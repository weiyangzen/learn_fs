# File Research: sources/os/linux/linux/fs/netfs/buffered_read.c

## Role

High-level buffered read support for network filesystems using the page cache. It manages readahead, `read_folio`, read-for-write prefetch, cache-vs-server source selection, zero filling beyond the readable point, rolling buffer setup, read subrequest queuing, and buffered `read_iter()` dispatch.

## Read Request Expansion and Cache Setup

- `netfs_cache_expand_readahead()` lets cache backends expand the requested readahead range.
- `netfs_rreq_expand()` lets both cache and filesystem expand readahead, then calls `readahead_expand()` so the VM includes the adjusted range.
- `netfs_begin_cache_read()` starts an FS-Cache read operation for the inode cookie through `fscache_begin_read_operation()`.

## Subrequest Preparation and Dispatch

- `netfs_prepare_read_iterator()` prepares a subrequest iterator from a rolling buffer or readahead control:
  - limits server reads by `sreq_max_len`;
  - loads folios from the readahead window into the rolling buffer;
  - limits by maximum segment count;
  - truncates `io_iter` and advances the rolling buffer.
- `netfs_cache_prepare_read()` asks the cache backend whether a slice should be read from cache, downloaded from server, or otherwise filled.
- `netfs_read_cache_to_pagecache()` submits a cache read into the pagecache iterator.
- `netfs_queue_read()` marks a subrequest in progress and appends it to the read stream with release ordering so the collector can safely consume it.
- `netfs_issue_read()` dispatches subrequests to server, cache, or zero-fill completion depending on `subreq->source`.

## Pagecache Read Engine

`netfs_read_to_pagecache()` slices a request into subrequests and for each slice:

- allocates a `netfs_io_subrequest`;
- queues it on the stream before preparing source state;
- asks FS-Cache for a source;
- for server reads, respects `netfs_read_zero_point()` and inode size, converting ranges beyond the zero point to zero-fill;
- calls optional filesystem `prepare_read()`;
- prepares iterators after source/length selection;
- marks `NETFS_RREQ_ALL_QUEUED` when the final slice is queued;
- handles pause/failure flags and wakes the collector on early exit;
- records deferred setup errors in `rreq->error`.

## Public Buffered Read Helpers

- `netfs_readahead()`
  - Allocates a read request for the readahead window.
  - Enables offloaded collection.
  - Begins cache access, records stats/traces, expands the request, initializes a destination rolling buffer, and calls `netfs_read_to_pagecache()`.
- `netfs_read_folio()`
  - Waits for writeback.
  - If the folio is dirty due to streaming writes, delegates to `netfs_read_gaps()`.
  - Otherwise creates a single-folio rolling buffer, reads the folio through cache/server/zero-fill, waits, and returns while unlocking the folio on error paths.
- `netfs_read_gaps()`
  - Reads only the clean gaps around a dirty streaming-write range in a folio.
  - Constructs a bvec array with the target folio for gaps and a temporary sink folio for the dirty middle range.
  - On success, restores group/private state, frees `netfs_folio` metadata, marks the folio uptodate, and flushes dcache.
- `netfs_write_begin()` `[DEPRECATED]`
  - Legacy write-begin helper that locks a folio, optionally calls filesystem conflict handling, skips reads for full/beyond-EOF writes when possible, otherwise preloads the folio through the read engine.
- `netfs_prefetch_for_write()`
  - Preloads a folio before buffered write when cache/content requirements need read-modify-write behavior.

## Read Iterator Dispatch

- `netfs_buffered_read_iter()` rejects direct/unbuffered state, brackets `filemap_read()` with `netfs_start_io_read()` / `netfs_end_io_read()`, and exports a buffered-only read path.
- `netfs_file_read_iter()` chooses unbuffered/direct read when `IOCB_DIRECT` is set or `NETFS_ICTX_UNBUFFERED` is active; otherwise it uses buffered reads.

## Dependencies

Uses `netfs_io_request`, `netfs_io_subrequest`, rolling buffers, folios, readahead controls, FS-Cache resources, filesystem netfs operations, tracepoints, stats counters, and read collector completion paths from other netfs files.

## Research Notes

The key abstraction is that a single pagecache read can be split into heterogeneous subrequests: cache reads, server downloads, and zero-fill segments. The file also bridges streaming writes back into coherent pagecache state by reading around dirty subranges rather than forcing full folio invalidation.
