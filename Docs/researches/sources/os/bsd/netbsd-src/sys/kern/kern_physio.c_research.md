# File Research: sources/os/bsd/netbsd-src/sys/kern/kern_physio.c

## Purpose
Implements raw physical I/O between user buffers and character devices, bypassing the buffer cache, with concurrent disk I/O support and asynchronous completion through a workqueue.

## Main Interfaces
- `physio(strategy, obp, dev, flags, min_phys, uio)`: maps user I/O vectors into buffers, locks user pages, calls device strategy routines, waits for completion, updates residuals/errors, and cleans up.
- `minphys(bp)`: default transfer-size clamp to `MAXPHYS`.

## Internal Helpers
- `physio_init`: creates `physiod` workqueue once.
- `physio_biodone`: strategy completion callback enqueues post-I/O work.
- `physio_done`: unmaps buffer, unlocks user pages, records errors/residuals, signals waiters, and releases temporary buffers.
- `physio_wait`: waits until outstanding request count is at or below a threshold.

## Internal State And Dependencies
- `physio_workqueue` and tunable `physio_concurrency = 16`.
- Per-call `struct physio_stat` tracks running I/Os, first/lowest-offset error, failures, residuals, original buffer, mutex, and CV.
- Uses buffer cache/iobuf APIs, `uvm_vslock/vsunlock`, `vmapbuf/vunmapbuf`, cdev type checks, workqueues, SDT, and process VM state.

## Control Flow Notes
- Disks can run multiple requests concurrently; non-disks and caller-supplied raw buffers force synchronous one-at-a-time behavior.
- Disk offsets must be `DEV_BSIZE` aligned and are split at `MAXPHYS`.
- Each request locks user pages with read/write permission opposite to the I/O direction, maps them into kernel space, sets `B_PHYS|B_RAW`, and calls `strategy`.
- Completion calculates earliest failing disk offset so `uio_resid` can be adjusted to represent data after the first failed region.

## Risk Areas
- `vmapbuf` clobbers `b_data` until `vunmapbuf`; cleanup ordering is critical.
- Partial completions and concurrent disk errors require careful lowest-offset accounting.
- Supplied `obp` is treated as a driver identifier by some drivers, so concurrency is disabled for that path.
- `min_phys` must not leave `b_bcount > MAXPHYS` in diagnostic builds.

## Filesystem Relevance
Direct storage relevance. Used by raw device I/O paths beneath filesystems and block devices, bypassing the buffer cache.
