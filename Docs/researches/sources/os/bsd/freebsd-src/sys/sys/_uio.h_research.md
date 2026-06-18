# File Research: sources/os/bsd/freebsd-src/sys/sys/_uio.h

UIO direction and segment enums.

Key elements:
- Under BSD visibility, defines `enum uio_rw` with `UIO_READ` and `UIO_WRITE`.
- Defines `enum uio_seg` for user space, system space, and no-copy segments.

Dependencies:
- Visibility macros from including context.

Research notes:
- UIO is central to VFS, device, socket, and filesystem I/O paths.
- This header only exports small enum pieces; full `struct uio` lives elsewhere.
