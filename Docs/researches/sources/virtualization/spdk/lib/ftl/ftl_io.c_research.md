# File Research: sources/virtualization/spdk/lib/ftl/ftl_io.c

## Purpose
Implements generic FTL user-IO descriptor helpers.

## Behavior
- Tracks inflight request counts with `ftl_io_inc_req()` and `ftl_io_dec_req()`.
- Provides LBA and iovec cursor helpers.
- `ftl_iovec_num_blocks()` validates block-size alignment and computes block count.
- `ftl_io_init()` zeroes and initializes an `ftl_io`, sets callback/user context, LBA, iovecs, type, invalid initial address, and trace ID.
- `ftl_io_complete()` clears initialized state, verifies/unpins L2P for pinned IO, and sends completion into the IO-channel completion ring.
- `ftl_io_cb()` handles error/retry logic; `-EAGAIN` reschedules reads, writes, or trims to the appropriate device queue.
- `ftl_io_fail()` marks a status and advances to completion.
- `ftl_io_clear()` resets cursor, status, flags, done state, and band pointer for retry.

## Important Safety Behavior
Pinned non-write IO verifies that current L2P entries still match the addresses read. If not, it converts completion to `-EAGAIN` so stale data is not returned.

## Dependencies
Uses FTL core, band, debug, L2P, mempool, trace, and SPDK rings through channel state.
