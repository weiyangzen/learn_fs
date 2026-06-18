# File Research: sources/os/linux/linux-stable/fs/netfs/buffered_write.c

## Purpose

`buffered_write.c` implements high-level buffered write helpers for network filesystems using pagecache folios. It supports normal buffered writes, writethrough writes for sync modes, streaming writes into not-yet-uptodate folios, cache-aware prefetch for partial writes, netfs folio grouping, inode size updates, and mmap page-mkwrite handling.

## Main Entry Points

- `netfs_perform_write(struct kiocb *iocb, struct iov_iter *iter, struct netfs_group *netfs_group)`
  - Core buffered write loop copying user data into pagecache folios.

- `netfs_buffered_write_iter_locked(struct kiocb *iocb, struct iov_iter *from, struct netfs_group *netfs_group)`
  - Removes file privileges, updates timestamps, then calls `netfs_perform_write()`.

- `netfs_file_write_iter(struct kiocb *iocb, struct iov_iter *from)`
  - Generic netfs `write_iter()` dispatcher.
  - Uses unbuffered/direct write for `IOCB_DIRECT` or `NETFS_ICTX_UNBUFFERED`; otherwise buffered path.

- `netfs_page_mkwrite(struct vm_fault *vmf, struct netfs_group *netfs_group)`
  - Handles mmap write faults and group transitions.

- `netfs_update_i_size(struct netfs_inode *ctx, struct inode *inode, loff_t pos, size_t copied)`
  - Updates inode size and approximates block count growth.

## Folio Acquisition

`netfs_grab_folio_for_write()`:

- Uses `__filemap_get_folio()` with `FGP_WRITEBEGIN`.
- Requests larger folios when the mapping supports them using `fgf_set_order()`.
- Chooses folio size based on write position and remaining chunk.

`netfs_perform_write()` uses `mapping_max_folio_size()` and iterates chunk-by-chunk until the source iterator is drained.

## Buffered Write Flow

For each chunk:

1. Fault in source user pages with `fault_in_iov_iter_readable()` before locking destination folio to avoid deadlocks.
2. Get and lock a target folio.
3. Wait for writeback if private netfs state exists.
4. Check signal interruption.
5. Read current netfs folio info/group.
6. Resolve group conflicts by flushing existing folio data if needed.
7. Choose write strategy:
   - Modify an uptodate folio.
   - Zero and fill beyond zero point.
   - Whole-folio write without pre-read.
   - Cache-enabled prefetch then modify.
   - Streaming write into an empty/non-uptodate folio.
   - Continue an existing streaming write.
   - Flush incompatible content and retry.
8. Update folio private/group state.
9. Mark uptodate if fully initialized.
10. Flush dcache, update inode size, advance position and written count.
11. Mark dirty or advance writethrough.
12. Balance dirty pages and reschedule.

## Streaming Write State

For non-cache streaming writes into folios that are not uptodate:

- A `struct netfs_folio` is allocated and stored in folio private data with `NETFS_FOLIO_INFO`.
- It records dirty offset, dirty length, and netfs group.
- Sequential continuation can extend the dirty range.
- If the write fills the whole folio, it is promoted to uptodate and the private info can be removed.
- Incompatible overlap/disjoint writes trigger writeback of existing content before retry.

This avoids read-modify-write when the workload writes forward and the local cache does not require a fully populated folio.

## Cache-Aware Behavior

When local caching is enabled:

- Streaming writes are avoided because cache consistency may require full folio contents.
- Existing `netfs_folio` state conflicts are flushed.
- `netfs_prefetch_for_write()` is used before copying into a non-uptodate folio.
- `NETFS_FOLIO_COPY_TO_CACHE` is handled as a special private marker distinct from a real netfs group.

## Writethrough Support

For `IOCB_DSYNC` or `IOCB_SYNC`:

- Existing dirty data in range is written and waited.
- `netfs_begin_writethrough()` creates a write request.
- Dirty folios are passed through `netfs_advance_writethrough()`.
- `netfs_end_writethrough()` finalizes and may return `-EIOCBQUEUED`.
- Writeback control is attached/detached around the operation.

This lets synchronous writes copy into pagecache while also issuing backing I/O.

## Inode Size Handling

`netfs_update_i_size()`:

- If filesystem provides `ctx->ops->update_i_size`, delegates.
- Otherwise takes `inode->i_lock`, updates `i_size`, updates FS-Cache cookie object size when enabled, and approximates `i_blocks`.
- Only grows size; it does not shrink.

The core write loop calls it after each successful copy.

## Generic Write Wrapper

`netfs_file_write_iter()`:

- Rejects zero-length writes early.
- Selects unbuffered/direct write if needed.
- Starts serialized netfs write I/O with `netfs_start_io_write()`.
- Runs `generic_write_checks()`.
- Calls buffered write locked helper.
- Ends netfs write serialization.
- Performs `generic_write_sync()` for positive results.

## mmap Page-Mkwrite

`netfs_page_mkwrite()`:

- Starts pagefault accounting with `sb_start_pagefault()`.
- Locks folio and waits for writeback.
- Requires folio to be uptodate.
- If group conflicts exist, writes back the folio and returns retry/OOM/SIGBUS as appropriate.
- Updates folio group/private state.
- Updates file time, marks modified attribute flag, and calls `post_modify()` if supplied.
- Returns `VM_FAULT_LOCKED` on success with folio locked.

## Error Handling

Important failure paths:

- Copy failure returns `-EFAULT` unless partial data was already written.
- Signal while blocked returns `-EINTR` after partial write or `-ERESTARTSYS` before any data.
- Allocation failures return `-ENOMEM`.
- Writeback or prefetch failures exit the loop.
- Function returns bytes written if any, otherwise negative error.

## Exports

Exports:

- `netfs_perform_write`
- `netfs_buffered_write_iter_locked`
- `netfs_file_write_iter`
- `netfs_page_mkwrite`

## Key Takeaways

This file is the buffered-write state machine for netfs. It balances pagecache semantics, network filesystem grouping, local cache requirements, streaming-write optimization, synchronous writethrough, and mmap write fault handling.
