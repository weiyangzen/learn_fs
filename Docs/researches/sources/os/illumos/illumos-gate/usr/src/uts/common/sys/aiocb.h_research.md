# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/aiocb.h

## Purpose

`aiocb.h` defines the user-visible asynchronous I/O control block structures and list-I/O constants.

## Main Types

`aiocb_t` contains file descriptor, buffer pointer, byte count, offset, request priority, signal/event notification, list-I/O opcode, embedded `aio_result_t`, state flag, and padding.

Large-file and syscall compatibility variants include `aiocb64_t` for userland large-file builds, `aiocb64_32_t` for 32-bit callers in the kernel, and `aiocb32_t` under `_SYSCALL32`. Packing pragmas preserve 32-bit alignment where required.

## Constants

The header defines `AIO_CANCELED`, `AIO_ALLDONE`, and `AIO_NOTCANCELED`; `LIO_NOWAIT` and `LIO_WAIT`; and list operation codes `LIO_NOP`, `LIO_READ`, and `LIO_WRITE`. The read/write values intentionally match `FREAD` and `FWRITE` without including `sys/file.h`.

## Research Notes

This is a stable user ABI file. Offset and pointer-size compatibility are the main maintenance concerns.
