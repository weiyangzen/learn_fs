# File Research: sources/os/linux/linux/fs/netfs/buffered_write.c

## Role

High-level buffered write support for netfs users. It copies user data into pagecache folios, supports large folios, tracks dirty subranges for streaming writes, handles writethrough for sync writes, updates inode size/block estimates, switches to unbuffered writes when required, and implements `page_mkwrite` handling for mmap writes.

## Inode Size Accounting

- `netfs_update_i_size()` updates inode size after copied data extends EOF.
- Filesystems may override size handling with `ctx->ops->update_i_size`.
- Default handling updates `i_size`, updates FS-Cache cookie size when enabled, and estimates `i_blocks` growth in sector units under `inode->i_lock`.

## Folio Selection and Write Strategy

- `netfs_grab_folio_for_write()` locks a folio for writing and requests the largest supported folio order for the target write chunk.
- `netfs_perform_write()` is the main buffered copy loop:
  - sets up writethrough state for `IOCB_DSYNC`/`IOCB_SYNC`;
  - faults user pages before locking destination folios to avoid deadlocks with same-page writes;
  - waits for writeback when folio private data is owned by writeback;
  - rejects interrupted waits appropriately;
  - handles group conflicts by flushing existing dirty content;
  - copies into uptodate folios directly;
  - zero-fills writes beyond `netfs_read_zero_point()`;
  - performs whole-folio modifications without prefetch where possible;
  - prefetches for write when local caching is enabled and read-modify-write is required;
  - creates or extends `struct netfs_folio` metadata for streaming dirty ranges;
  - flushes and retries incompatible overlapping streaming writes;
  - marks fully covered folios uptodate and dirty or advances writethrough state.
- Dirty folios can carry either a filesystem group, the `NETFS_FOLIO_COPY_TO_CACHE` marker, or `struct netfs_folio` metadata describing a partial dirty range and group.

## Buffered Write Entry Points

- `netfs_buffered_write_iter_locked()`
  - Assumes caller already holds appropriate locks and ran generic write checks.
  - Removes file privileges, updates modification time, then calls `netfs_perform_write()`.
- `netfs_file_write_iter()`
  - Returns immediately for zero-length writes.
  - Uses `netfs_unbuffered_write_iter()` for direct I/O or `NETFS_ICTX_UNBUFFERED`.
  - Otherwise brackets `generic_write_checks()` and buffered write with `netfs_start_io_write()` / `netfs_end_io_write()`.
  - Calls `generic_write_sync()` after successful buffered writes.

## Writethrough and Sync Handling

For sync writes, `netfs_perform_write()` attaches a `writeback_control`, waits for prior data in range, starts a writethrough request, advances it as folios are copied, ends writethrough after the loop, and can return `-EIOCBQUEUED` for async completion.

## mmap Write Faults

`netfs_page_mkwrite()`:

- brackets the fault with `sb_start_pagefault()` / `sb_end_pagefault()`;
- locks the folio and waits for writeback;
- requires the folio to be uptodate;
- flushes and retries if an incompatible group is already attached;
- adjusts folio private group/copy-to-cache state;
- updates file time and modified-attribute state;
- calls optional `post_modify()`;
- returns `VM_FAULT_LOCKED` on success.

## Dependencies

Uses Linux folio/pagecache APIs, writeback control, dirty throttling, generic write checks/sync, FS-Cache cookie updates, netfs group/private folio helpers, writethrough helpers, tracepoints, and direct/unbuffered write entry points.

## Research Notes

The file is optimized to avoid unnecessary read-modify-write cycles while preserving correctness for local caching, content transformations, mmap writes, and filesystem grouping such as snapshots. The `netfs_folio` dirty-range metadata is central: it lets netfs track streaming writes into not-yet-uptodate folios and later read only gaps or flush conflicting ranges.
