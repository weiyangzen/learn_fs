# File Research: sources/os/bsd/openbsd-src/sys/sys/uio.h

Defines vectored I/O structures. Public `struct iovec` contains base pointer and length. BSD-visible enums identify read/write direction and user/system address space; kernel `struct uio` adds iovec array, count, file offset, residual bytes, segment flag, direction, and associated process.

Userland prototypes include `readv`, `writev`, and BSD `preadv`/`pwritev`. Kernel prototypes include `ureadc`, iovec copy/free helpers, and file readv/writev syscall helpers. VFS and tty paths use this as the standard scatter/gather I/O carrier.
