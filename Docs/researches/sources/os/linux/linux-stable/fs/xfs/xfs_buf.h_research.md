# File Research: sources/os/linux/linux-stable/fs/xfs/xfs_buf.h

## Purpose

Defines the XFS buffer cache public API, flags, core structures, and inline helpers.

## Main Types

- `struct xfs_buftarg`
  - block/DAX target
  - mount pointer
  - sector geometry
  - LRU/shrinker state
  - readahead counter
  - atomic write geometry
  - buffer hash table
- `struct xfs_buf_map`
  - disk address
  - length
  - lookup flags
- `struct xfs_buf_ops`
  - verifier name
  - v4/v5 magic values
  - read/write verifier callbacks
  - structural verifier callback
- `struct xfs_buf`
  - cache hash node and key
  - length and maps
  - lockref and semaphore
  - LRU state
  - perag/mount/target pointers
  - backing address
  - I/O completion state
  - log item hooks
  - pin count
  - error/retry tracking
  - verifier ops

## Main APIs

- Lookup/read:
  - `xfs_buf_get_map`
  - `xfs_buf_read_map`
  - `xfs_buf_readahead_map`
  - `xfs_buf_get`
  - `xfs_buf_read`
  - `xfs_buf_incore`
- Uncached buffers:
  - `xfs_buf_get_uncached`
  - `xfs_buf_read_uncached`
- Lifetime and locking:
  - `xfs_buf_hold`
  - `xfs_buf_rele`
  - `xfs_buf_trylock`
  - `xfs_buf_lock`
  - `xfs_buf_unlock`
  - `xfs_buf_relse`
- I/O and errors:
  - `xfs_bwrite`
  - `xfs_buf_ioerror`
  - `xfs_buf_ioerror_alert`
  - `xfs_buf_ioend_fail`
  - `xfs_buf_mark_corrupt`
- Utilities:
  - `xfs_buf_offset`
  - `xfs_buf_zero`
  - `xfs_buf_stale`
  - `xfs_buf_daddr`
  - checksum verify/update helpers
- Delayed write:
  - `xfs_buf_delwri_cancel`
  - `xfs_buf_delwri_queue`
  - `xfs_buf_delwri_queue_here`
  - `xfs_buf_delwri_submit`
  - `xfs_buf_delwri_submit_nowait`
- Buftarg:
  - `xfs_alloc_buftarg`
  - `xfs_free_buftarg`
  - `xfs_buftarg_wait`
  - `xfs_buftarg_drain`
  - `xfs_configure_buftarg`
  - `xfs_init_buftarg`
  - `xfs_destroy_buftarg`

## Important Flags

- `XBF_READ`, `XBF_WRITE`
- `XBF_READ_AHEAD`
- `XBF_ASYNC`
- `XBF_DONE`
- `XBF_STALE`
- `XBF_WRITE_FAIL`
- `_XBF_LOGRECOVERY`
- `_XBF_KMEM`
- `_XBF_DELWRI_Q`
- lookup-only flags: `XBF_LIVESCAN`, `XBF_INCORE`, `XBF_TRYLOCK`

## Research Notes

This header is the main contract for XFS metadata buffer users. Callers must respect ownership rules around locked buffers, delayed-write references, and async I/O completion.
