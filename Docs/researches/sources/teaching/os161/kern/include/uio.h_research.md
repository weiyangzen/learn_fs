# File Research: sources/teaching/os161/kern/include/uio.h

Defines BSD-style `struct uio`, the kernel abstraction for moving data between kernel buffers and user or kernel memory while tracking offset and residual byte count. It uses `struct iovec`, `uio_iovcnt`, `uio_offset`, `uio_resid`, segment flag, read/write direction, and associated address space.

Directions are `UIO_READ` and `UIO_WRITE`; segments distinguish user instruction space, user data space, and kernel space. Exports `uiomove`, `uiomovezeros`, and `uio_kinit`.

Important semantics: `uiomove` mutates iovec fields, increments `uio_offset`, decrements `uio_resid`, and requires the active address space to match `uio_space` for user transfers. Directory offsets may be filesystem cookies, not byte counts.
