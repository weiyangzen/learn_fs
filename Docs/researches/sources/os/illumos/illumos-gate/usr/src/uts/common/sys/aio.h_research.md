# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/aio.h

## Purpose

`aio.h` defines common asynchronous I/O result types and legacy/Solaris AIO operation codes.

## Main Types

`aio_result_t` carries the return value and errno for an asynchronous operation. A 32-bit syscall variant, `aio_result32_t`, is provided under `_SYSCALL32`.

## Operation Codes

The header defines opcodes for read, write, wait, cancel, notify, init, start, list I/O, suspend, error, list wait, asynchronous read/write, fsync, waitn, and reserved implementation operations. Large-file 64-bit opcode aliases differ depending on LP64 versus ILP32 build mode.

`AIO_POLL_BIT` is the opcode filter for `AIO_INPROGRESS`.

## Research Notes

This is a small ABI header that feeds both POSIX AIO and older Solaris AIO compatibility layers. It is relevant to filesystem research because AIO requests ultimately drive vnode/device I/O paths.
