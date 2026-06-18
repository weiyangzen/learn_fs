# File Research: sources/os/bsd/freebsd-src/sys/sys/aio.h

POSIX asynchronous I/O public and kernel definitions.

Key elements:
- Defines AIO cancellation results, LIO opcodes/modes, vectored and file-offset extensions, and `AIO_LISTIO_MAX`.
- Defines public `struct aiocb` and `aiocb_t`, with aliases for vectored I/O.
- Under `_KERNEL`, defines worker pool tunables, backend function types, `struct kaiocb`, and AIO backend lifecycle/cancellation APIs.
- Userland declares `aio_read`, `aio_write`, `lio_listio`, `aio_error`, `aio_return`, `aio_cancel`, `aio_suspend`, `aio_mlock`, `aio_fsync`, and BSD extensions.

Dependencies:
- Includes `sys/types.h` and `sys/signal.h`; kernel includes queue, event, signalvar, and uio headers.

Research notes:
- Directly relevant to asynchronous filesystem and block I/O.
- `struct kaiocb` stores copied user control block, UIO/iovec storage, credentials, file pointer, notification state, and backend-specific state.
