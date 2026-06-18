# File Research: sources/os/bsd/dragonflybsd/sys/kern/kern_physio.c

This file implements `physread()` and `physwrite()` through a shared `physio()` helper for character devices. It turns user or kernel `uio` vectors into synchronous buffer I/O requests sent to the device strategy routine.

Important behavior:
- Uses `getpbuf_mem()` for userspace I/O and `getpbuf_kva()` for kernel-space I/O.
- Warns and resets `dev->si_iosize_max` to `MAXPHYS` if the device reports a maximum below `PAGE_SIZE`.
- Rejects `UIO_NOCOPY` through `KKASSERT`.
- Iterates every iovec and breaks it into chunks no larger than the device limit and pbuf KVA size.
- For userspace writes, copies data into the pbuf before strategy; for userspace reads, copies completed data back after `biowait()`.
- Sets `bp->b_bio1.bio_offset`, synchronous completion callback, and `BIO_SYNC`, then calls `dev_dstrategy()`.
- Updates `uio` base, length, residual, and offset based on bytes actually completed.

Error handling:
- If the transfer completes zero bytes without `B_ERROR`, it treats that as EOF and exits.
- Device errors are propagated from `bp->b_error`.
- The pbuf is released on all exit paths.

Filesystem/storage relevance:
- This is directly storage-facing generic raw device I/O glue. It is relevant to block/character device access used below or beside filesystems.
