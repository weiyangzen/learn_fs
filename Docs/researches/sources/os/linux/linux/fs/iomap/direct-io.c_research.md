# File Research: sources/os/linux/linux/fs/iomap/direct-io.c

Implements iomap-based direct I/O read/write submission and completion. The central object is `struct iomap_dio`, which tracks the `kiocb`, filesystem DIO ops, byte counts, private flags, error state, references for in-flight bios, and either synchronous wait state or async completion work.

Key entry points:
- `__iomap_dio_rw()` creates and submits a direct I/O request and can return a queued `ERR_PTR(-EIOCBQUEUED)`, a completed `iomap_dio`, `NULL`, or an error.
- `iomap_dio_rw()` wraps `__iomap_dio_rw()` and immediately completes synchronous results through `iomap_dio_complete()`.
- `iomap_dio_complete()` applies filesystem `end_io`, reports fs errors, advances `ki_pos`, handles short reads, post-write invalidation, DSYNC writeback, and frees the DIO object.
- `iomap_dio_bio_end_io()` and `iomap_finish_ioend_direct()` bridge block/ioend completions back to DIO refcounting.

Submission flow:
- `__iomap_dio_rw()` initializes `iomap_iter` with `IOMAP_DIRECT`, adds `IOMAP_NOWAIT`, `IOMAP_WRITE`, `IOMAP_ATOMIC`, or `IOMAP_OVERWRITE_ONLY` as needed, invalidates cached pages for writes, initializes the superblock DIO done workqueue for async completions, calls `inode_dio_begin()`, and iterates mappings with `iomap_iter()`.
- `iomap_dio_iter()` dispatches mapping types: holes and unwritten reads are zero-filled, mapped/unwritten writes submit bios, inline extents use iter copy helpers, and delalloc collisions warn and fail.
- `iomap_dio_bio_iter()` validates alignment, selects logical block or filesystem block alignment, handles unwritten/new/shared extents, atomic bio requirements, write-through/FUA optimization, completion-work requirements, sub-block zeroing before and after writes, and iov truncation per extent.
- `iomap_dio_bio_iter_one()` allocates a bio, sets crypto/integrity/ioprio/write hints, pins or bounces iov pages, accounts write bytes, marks user read pages dirty when needed, disables polling for multi-bio I/O, and submits via filesystem `submit_io` or `blk_crypto_submit_bio()`.

Completion behavior:
- Refcounting allows submission and all bio completions to race safely. The final reference calls `iomap_dio_done()`.
- Synchronous completions wake the submitting task; async completions either complete inline or are queued to `s_dio_done_wq`.
- Error completions and writes needing page invalidation or filesystem metadata completion are forced into workqueue context.
- `IOMAP_DIO_WRITE_THROUGH` can suppress later generic sync when all issued writes are FUA or do not need volatile-cache flushes.
- Magic errors `-EAGAIN` and `-ENOTBLK` are treated specially for retry/fallback and not reported through fs error notifications.

Important dependencies:
- Uses iomap iteration from `iter.c`.
- Direct ioend completions are finished by `ioend.c`.
- Tracepoints come from `trace.h`.
- Depends on block crypto, fscrypt bio contexts, bio integrity generation/verification, page-cache invalidation helpers, and `inode_dio_begin/end`.
