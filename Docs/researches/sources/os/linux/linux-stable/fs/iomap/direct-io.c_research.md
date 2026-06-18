# File Research: sources/os/linux/linux-stable/fs/iomap/direct-io.c

Implements iomap direct I/O submission and completion for reads and writes. The central state is `struct iomap_dio`, which tracks the kiocb, filesystem DIO ops, byte counts, i_size snapshot, async/sync completion state, private flags, and first error.

Key paths:
- `__iomap_dio_rw()` prepares the DIO, handles NOWAIT, read/write setup, page-cache invalidation for writes, sync/FUA policy, `inode_dio_begin()`, and iterates mappings with `iomap_iter()`.
- `iomap_dio_iter()` dispatches by iomap type: holes and unwritten reads zero the iterator, mapped/unwritten writes submit bios, inline data copies directly, DELALLOC collisions warn and fail.
- `iomap_dio_bio_iter()` validates alignment, handles new/unwritten/shared extents, atomic bio requirements, write-through/FUA decisions, zeroes sub-block head/tail regions, and submits one or more bios.
- `iomap_dio_bio_end_io()` and `iomap_finish_ioend_direct()` feed bio/ioend completion back into the shared DIO refcount.
- `iomap_dio_complete()` calls filesystem `end_io`, reports fs errors, adjusts short reads to i_size, performs post-write invalidation, ends inode DIO, updates `ki_pos`, and runs write sync if required.

Important invariants:
- Private DIO flags live above public `iomap.h` flag bits.
- Completion can occur inline, on `s_dio_done_wq`, or synchronously by waking the submitter.
- Async errors are forced to workqueue context because filesystem error completion may sleep.
- Polling is only allowed for single-bio non-sync DIO and is cleared once multiple bios or completion work are needed.
- `-ENOTBLK` is a magic fallback-to-buffered-write result and is not reported as an fsnotify I/O error.
- Atomic writes require one full-length bio for the mapped range.

Dependencies:
- Uses `iomap_iter()` from `iter.c`, ioend completion from `ioend.c`, tracepoints from `trace.h`, fscrypt, block integrity, bio bouncing, page-cache invalidation helpers, and filesystem callbacks in `struct iomap_dio_ops`.
