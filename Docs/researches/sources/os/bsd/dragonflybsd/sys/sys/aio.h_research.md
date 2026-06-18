# File Research: sources/os/bsd/dragonflybsd/sys/sys/aio.h

Read completely: 148 lines.

This header defines POSIX asynchronous I/O constants, control blocks, and prototypes.

Key contents:
- `aio_cancel` status constants.
- `LIO_*` opcodes and modes.
- `AIO_LISTIO_MAX` of 16.
- `aiocb_t` with file descriptor, offset, user buffer, byte count, sigevent, lio opcode, ignored priority, and internal result/error fields.
- Userland prototypes for `aio_read`, `aio_write`, `lio_listio`, `aio_error`, `aio_return`, `aio_cancel`, `aio_suspend`, `aio_fsync`, and `aio_waitcomplete`.

Security/reliability notes:
- No implementation logic. The `aiocb` layout and volatile buffer pointer are ABI-sensitive.
- Correct use requires exactly one `aio_return()` per submitted control block, as noted by the comments.
