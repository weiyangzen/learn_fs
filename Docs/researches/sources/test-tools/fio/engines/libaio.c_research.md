# sources/test-tools/fio/engines/libaio.c

## Purpose
Implements fio's Linux native AIO engine through libaio. It batches `io_u` requests into an internal ring, submits them with `io_submit()`, reaps completions via `io_getevents()` or an optional user-space ring reader, and exposes options for `RWF_NOWAIT`, vectored AIO, and command-priority injection.

## Important APIs, Types, And Functions
`struct libaio_data` owns the AIO context, completion event buffer, queued IOCB pointers, matching `io_u` pointers, per-depth iovecs, circular queue indexes, and `struct cmdprio`. `struct libaio_options` provides `userspace_reap`, `nowait`, `libaio_vectored`, and `cmdprio` settings. Key functions are `fio_libaio_init()`, `fio_libaio_post_init()`, `fio_libaio_prep()`, `fio_libaio_queue()`, `fio_libaio_commit()`, `fio_libaio_getevents()`, `fio_libaio_event()`, and `fio_libaio_cleanup()`.

## Control Flow
`init` allocates buffers sized by `iodepth` and initializes command priority; `post_init` creates the kernel AIO context. `prep` encodes read/write IOCBs as either pread/pwrite or preadv/pwritev and sets `RWF_NOWAIT` or `RWF_ATOMIC` where supported. `queue` rejects when the internal ring is full, handles trim/syncfs synchronously if no queued AIO is outstanding, applies command priority, and appends the IOCB to the ring. `commit` submits contiguous ring spans, tracks issue time, advances the tail, and handles `EAGAIN`, `EINTR`, and `ENOMEM`. `getevents` loops until the requested minimum is met or errors occur, optionally reading the kernel completion ring directly when `userspace_reap` is safe.

## State And Persistence
Persistent state is the kernel AIO context plus queued-but-not-submitted IOCBs. User data is stored in fio's `io_u` IOCB member, so completion maps back with `container_of(ev->obj, struct io_u, iocb)`. File data is handled by generic fio file open/close/size operations.

## Dependencies And Integration Points
Depends on libaio, Linux `aio_abi` fields, fio's `cmdprio`, `io_u` lifecycle, generic file helpers, and fio issue-time accounting. It registers a single `libaio` `ioengine_ops`.

## Risks
The user-space reap path depends on kernel AIO ring layout and magic. `fio_libaio_commit()` has careful handling for partial submissions and transient resource failures; regressions can strand queued IOCBs. Trim and syncfs are synchronous only when the queue is empty. `aio_rw_flags` compatibility uses a preprocessor alias for older libaio headers.

## Test Signals
Exercise normal and vectored reads/writes, mixed queue depths, `iodepth_batch_complete_min=0`, `userspace_reap`, `nowait`, command-priority percentages, trim and syncfs interleaved with queued AIO, `EAGAIN`/resource-pressure behavior, and atomic writes when `FIO_HAVE_RWF_ATOMIC` is available.
