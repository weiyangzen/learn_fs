# sources/test-tools/fio/engines/ftruncate.c

Purpose: Implements a fake synchronous `ftruncate` engine that models writes by truncating files to requested offsets.

Important APIs/functions: `fio_ftruncate_queue()` is the main queue callback; the engine uses generic file open/close/size and flags `FIO_SYNCIO | FIO_FAKEIO | FIO_SYNCFS`.

Control flow: Queue performs read-only checks, calls `ftruncate(f->fd, io_u->offset)` for write directions, delegates sync directions to `do_io_u_sync()`, rejects other directions with `EINVAL`, and maps syscall failures to `io_u->error`.

State/persistence: File size changes persist on disk. No extra engine state is allocated.

Dependencies/integration: POSIX `ftruncate`, fio generic file lifecycle, sync helpers, and fake-IO semantics.

Risks: It truncates to `offset`, not `offset + xfer_buflen`, so fio write sizes influence accounting but not final length directly. No data is written, making verify workloads inappropriate.

Test signals: Verify write offsets produce expected file sizes, sync paths work, unsupported directions fail, and generic open/close integration is clean.
