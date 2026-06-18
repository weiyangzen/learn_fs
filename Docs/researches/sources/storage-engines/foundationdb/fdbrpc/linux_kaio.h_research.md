# sources/storage-engines/foundationdb/fdbrpc/linux_kaio.h

## Purpose

`linux_kaio.h` is a small Linux native asynchronous I/O syscall shim for FoundationDB's `AsyncFileKAIO` implementation. It avoids relying on a separate libaio wrapper by declaring the kernel IOCB/result structures and thin syscall functions.

## Important APIs, types, and functions

The file defines `io_context_t` as `struct io_context*`, operation constants `IO_CMD_PREAD`, `IO_CMD_PWRITE`, `IO_CMD_FSYNC`, and `IO_CMD_FDSYNC`, `struct linux_iocb`, `struct linux_ioresult`, and static wrappers `io_setup()`, `io_submit()`, and `io_getevents()`. `linux_iocb` includes user data, opcode, priority, fd, buffer, byte count, offset, flags, and eventfd; `linux_ioresult` returns user data, original IOCB pointer, result, and secondary result.

## Control flow, state, and persistence

The wrappers directly call `syscall(__NR_io_setup)`, `syscall(__NR_io_submit)`, and `syscall(__NR_io_getevents)`. The header stores no state; kernel AIO state is held in the `io_context_t` owned by `AsyncFileKAIO`.

## Dependencies and integration points

`AsyncFileKAIO.h` includes this header, initializes a context with `io_setup(FLOW_KNOBS->MAX_OUTSTANDING, ...)`, submits arrays of `linux_iocb*`, and collects `linux_ioresult` events. The header assumes syscall numbers, `syscall()`, `uint*_t`, `timespec`, and related Linux types are available from the including translation unit.

## Risks and test signals

The struct layout must match the Linux kernel ABI exactly. Return values from raw syscalls are negative error codes rather than libc-style `-1` with `errno` in some paths, and callers must handle that carefully. Kernel AIO has filesystem and alignment limitations, and this header does not wrap `io_destroy()`. Test with `AsyncFileKAIO` read/write/fsync/truncate workloads, eventfd polling, error paths such as `EAGAIN`, and Linux ABI compatibility across supported architectures.
