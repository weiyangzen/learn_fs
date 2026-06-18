# File Research: sources/os/bsd/freebsd-src/sys/sys/uio.h

Scatter/gather I/O vector and kernel `uio` movement interface.

Key responsibilities:
- Includes shared `iovec` and private `_uio` enum definitions.
- Defines `ssize_t` and `off_t` if needed.
- Under `_KERNEL`, defines `struct uio` with iovec array, count, target offset, residual byte count, segment flag, read/write direction, and owning thread.
- Defines `UIO_MAXIOV` as 1024.
- Declares allocation, free, clone, iovec/uio copyin, mapped copyout, external error copyout, physical copyin/copyout, bus-DMA-vector physical copy, `uioadvance`, and `uiomove` variants for buffers, physical pages, nofault memory, and VM objects.
- In userland, declares `readv`, `writev`, and BSD-visible `preadv`/`pwritev`, using fortified wrappers when enabled.

Dependencies:
- Includes `sys/cdefs.h`, `_types`, `_iovec`, and `_uio`; kernel APIs depend on thread, VM object/page, and bus DMA segment types.

Notable risks:
- `uio_resid`, offsets, and iovec counts drive copy loops throughout filesystems and device drivers; overflow and partial-copy behavior are critical.
- The `UIO_MAXIOV` comment ties the constant to public `IOV_MAX` compatibility expectations.
