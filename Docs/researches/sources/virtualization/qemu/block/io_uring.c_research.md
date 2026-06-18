# File Research: sources/virtualization/qemu/block/io_uring.c

## Role

`block/io_uring.c` provides QEMU's Linux `io_uring` coroutine submission backend for block/file I/O. It converts QEMU raw AIO request types into liburing SQEs, waits for CQE completion through QEMU's AioContext infrastructure, and resumes the submitting coroutine.

## Core Data Structure

`LuringRequest` is stack allocated by `luring_co_submit()` and carries:
- submitting coroutine,
- target `QEMUIOVector`,
- file descriptor,
- byte offset,
- request type,
- request flags,
- result,
- short-I/O progress,
- resubmission iovec,
- `CqeHandler`.

Because the request lives on the coroutine stack, completion wakes the same coroutine rather than invoking an arbitrary user callback.

## Submission

`luring_co_submit()` initializes `LuringRequest`, sets its CQE handler, calls `aio_add_sqe()`, and yields while `req.ret == -EINPROGRESS`. Completion sets `req.ret` and wakes the coroutine unless it is already entered.

`luring_prep_sqe()` builds the actual SQE:
- `QEMU_AIO_WRITE`: uses `io_uring_prep_writev2` with `RWF_DSYNC` for FUA when available, otherwise writev/write.
- `QEMU_AIO_ZONE_APPEND`: currently submits writev at the supplied offset.
- `QEMU_AIO_READ`: uses readv/read depending on vector count.
- `QEMU_AIO_FLUSH`: uses `io_uring_prep_fsync(..., IORING_FSYNC_DATASYNC)`.

Single-element iovecs use non-vectored read/write because the code notes those are faster according to the man page.

## Completion and Retry Behavior

`luring_cqe_handler()` translates CQE results to QEMU status:
- `-EINTR` and `-EAGAIN` are immediately resubmitted. The comment says `-EAGAIN` is not expected for regular files or host block devices but is known with Linux SCSI.
- Full read/write completion returns `0`.
- Short reads and writes are resubmitted with `luring_resubmit_short_io()`.
- Read EOF pads the remaining buffer with zeroes and succeeds.
- Write returning zero, or zone append returning fewer bytes than requested, becomes `-ENOSPC`.

`luring_resubmit_short_io()` advances `total_done`, builds a sliced `resubmit_qiov`, and submits another SQE for the remaining range.

## FUA Support

`luring_has_fua()` returns true only when QEMU was built with `HAVE_IO_URING_PREP_WRITEV2`. Without that API, FUA must not be requested through this backend; the write path asserts that `RWF_DSYNC` is zero.

## Integration Points

This file is selected by Meson when `linux_io_uring` is available. Higher-level block code, usually through raw/file backends, calls `luring_co_submit()` for coroutine-style I/O.
