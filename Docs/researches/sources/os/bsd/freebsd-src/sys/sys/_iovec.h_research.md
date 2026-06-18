# File Research: sources/os/bsd/freebsd-src/sys/sys/_iovec.h

Scatter/gather vector definition.

Key elements:
- Declares `size_t` if needed.
- Defines `struct iovec` with `iov_base` and `iov_len`.
- Under `_KERNEL`, adds initialization and advancement helper macros.

Dependencies:
- Includes `sys/_types.h`.
- Kernel helpers rely on `strlen()` and `KASSERT()` being available from including context.

Research notes:
- Core ABI for read/write, VFS, socket, and block I/O scatter/gather paths.
- `IOVEC_ADVANCE` bounds-checks advancement before adjusting pointer and length.
