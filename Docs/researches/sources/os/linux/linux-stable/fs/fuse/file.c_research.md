# File Research: sources/os/linux/linux-stable/fs/fuse/file.c

## Purpose

`file.c` implements FUSE regular-file operations: open/release, flush/fsync, buffered reads and writes, direct I/O, writeback, mmap, locking, lseek, poll, fallocate, splice, passthrough dispatch, DAX dispatch, and copy-file-range.

## Main Responsibilities

- Sends `FUSE_OPEN`/`FUSE_OPENDIR` and manages `struct fuse_file` handles.
- Sends delayed or synchronous `FUSE_RELEASE`/`FUSE_RELEASEDIR`.
- Implements `flush`, `fsync`, and writeback synchronization.
- Implements cached reads through iomap read helpers and FUSE read requests.
- Implements cached writes either through writeback-cache/iomap or immediate FUSE writes.
- Implements direct I/O with sync/async request splitting, page extraction, completion aggregation, and EOF/short-I/O handling.
- Implements writeback batching for dirty folios using iomap writeback callbacks.
- Supports DAX and passthrough dispatch where negotiated.
- Implements mmap behavior, including direct-I/O shared mmap restrictions.
- Implements POSIX locks, flock, bmap, lseek, poll notification, fallocate, and copy-file-range.

## Open and Release Lifecycle

`fuse_file_open()` allocates `struct fuse_file`, optionally sends `FUSE_OPEN` or `FUSE_OPENDIR`, records server file handle and `FOPEN_*` flags, and detects `-ENOSYS` no-open/no-opendir support. Regular files still allocate release argument storage even in no-open mode to avoid reclaim deadlocks with pending I/O.

`fuse_finish_open()` finalizes cache/passthrough I/O mode through `fuse_file_io_open()`, applies stream/nonseekable flags, and links writable files into `fi->write_files` when writeback cache is enabled.

`fuse_prepare_release()` removes the file from write and poll tracking, wakes poll waiters, prepares the release request, and optionally pins the inode until async release completion. `fuse_file_put()` sends release synchronously or in background after outstanding async I/O drops references.

## Flush and Fsync

`fuse_flush()` writes dirty inode data, checks mapping errors, sends `FUSE_FLUSH` unless unsupported or suppressed by `FOPEN_NOFLUSH`, and invalidates block count attributes in writeback-cache mode.

`fuse_fsync()`:
- Locks the inode.
- Calls `file_write_and_wait_range()`.
- Waits for queued/sent FUSE writepages via `fuse_sync_writes()`.
- Checks writeback errors directly.
- Syncs inode metadata.
- Sends `FUSE_FSYNC` unless unsupported.

Directory fsync in `dir.c` reuses `fuse_fsync_common()` with `FUSE_FSYNCDIR`.

## Cached Reads

Cached read uses iomap:
- `fuse_read_folio()` handles synchronous folio reads.
- `fuse_readahead()` batches folios and may issue async background reads if `async_read` is enabled.
- `fuse_send_readpages()` sends multi-folio `FUSE_READ` requests.
- `fuse_readpages_end()` completes folios and handles short reads.
- `fuse_short_read()` treats short reads as EOF unless writeback cache is enabled, where holes can be hidden by dirty local cache.

`fuse_cache_read_iter()` refreshes size on auto-invalidate mounts or reads beyond cached EOF, then delegates to `generic_file_read_iter()`.

## Cached Writes

There are two buffered write modes:
- With writeback cache and no killpriv conflict, `fuse_cache_write_iter()` uses `iomap_file_buffered_write()` for granular dirty tracking.
- Otherwise, `fuse_perform_write()` copies user data into cache folios and sends `FUSE_WRITE` immediately.

`fuse_write_update_attr()` increments attribute version, extends local i_size when needed, and invalidates size/mtime/ctime/block attributes.

Immediate writes use `fuse_fill_write_pages()` and `fuse_send_write_pages()`. They wait on folio writeback, copy data atomically from the iterator, send `FUSE_WRITE`, clear uptodate on error/short write, unlock the last locked folio when needed, and update position only for completed bytes.

## Direct I/O

`fuse_direct_io()` is the shared direct read/write engine:
- Splits I/O by `max_read`/`max_write` and `max_pages`.
- Extracts user pages with `iov_iter_extract_pages()` or uses kvec buffers directly when allowed.
- Handles vmalloc kernel I/O flushing/invalidation.
- Sends `FUSE_READ` or `FUSE_WRITE`.
- Supports async completion through `struct fuse_io_priv`.
- Reverts iov_iter on short or failed operations.
- Invalidates page cache around `FOPEN_DIRECT_IO` writes.

Direct writes use `fuse_dio_lock()`:
- Exclusive lock for append, past-EOF writes, non-parallel direct-write servers, or cached I/O mode.
- Shared lock for negotiated parallel direct writes, guarded by uncached I/O mode counters.

`fuse_direct_IO()` is the address-space direct-I/O hook and supports async DIO. It avoids async extending writes, truncates back after failed extending writes, and handles short-read truncation optimizations.

## Writeback

Writeback uses `struct fuse_writepage_args` and iomap writeback callbacks:
- `fuse_iomap_writeback_range()` batches contiguous dirty ranges until max pages, max bytes, or discontinuity.
- `fuse_writepages_send()` queues batches on `fi->queued_writes`.
- `fuse_flush_writepages()` sends queued batches only while no truncate/fsync write exclusion is active.
- `fuse_send_writepage()` submits background forced/nocreds write requests and respects current inode size crop.
- `fuse_writepage_end()` records mapping errors, invalidates modification attrs when not writeback-cache, decrements write counters, completes folio writeback, and frees resources.

`fuse_launder_folio()` writes one dirty folio and waits for writeback before reclaim/laundering.

## mmap and I/O Mode

`fuse_file_mmap()` dispatches:
- DAX mmap to `fuse_dax_mmap()`.
- Passthrough mmap to `fuse_passthrough_mmap()`.
- Direct-I/O mmap only when restrictions allow it.

For `FOPEN_DIRECT_IO`, shared mmap requires `FUSE_DIRECT_IO_ALLOW_MMAP`. The first shared mmap transitions the inode into cached I/O mode and waits out incompatible parallel direct writers.

`fuse_page_mkwrite()` updates file time, locks the folio, verifies mapping, and waits for prior writeback before allowing the page to be dirtied again.

## Locks, Poll, Lseek, and Other File Ops

- POSIX locks use `FUSE_GETLK`, `FUSE_SETLK`, and `FUSE_SETLKW`; fallback uses local locks if server lacks support.
- `flock` uses FUSE lock requests with `FUSE_LK_FLOCK`, or local fallback if unsupported.
- `fuse_lseek()` uses `FUSE_LSEEK` for `SEEK_DATA`/`SEEK_HOLE`, falling back to generic seek after refreshing size.
- Poll registers `struct fuse_file` in an rb-tree keyed by kernel handle and wakes waiters on `FUSE_NOTIFY_POLL`.
- `fuse_file_fallocate()` sends `FUSE_FALLOCATE`, coordinates writeback and DAX layout breakage, updates size, and truncates page cache for hole-punch/zero-range.
- `fuse_copy_file_range()` uses `FUSE_COPY_FILE_RANGE_64` with fallback to older `FUSE_COPY_FILE_RANGE`, then splice fallback for unsupported/exdev cases.

## Operation Tables

`fuse_file_operations` provides regular file VFS methods. `fuse_file_aops` provides folio read/readahead/writeback/dirty/invalidate/bmap/direct-I/O behavior.

`fuse_init_file_inode()` installs these operations and initializes writeback, direct-I/O, and optional DAX inode state.

## Edge Cases and Risks

- Release may be delayed until async I/O completes.
- Direct-I/O async completion must aggregate partial request results into the longest contiguous transferred prefix.
- Writeback cache changes which timestamps and sizes can be trusted from userspace replies.
- Mixing passthrough, cached I/O, direct I/O, shared mmap, and DAX requires careful mode transitions.
- Copy-file-range cache invalidation can lose unusual concurrent mmap writes to partial pages, as documented in-code.
