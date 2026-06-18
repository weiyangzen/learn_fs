# File Research: sources/os/bsd/netbsd-src/sys/sys/uio.h

Read completely: 123 lines.

Defines scatter/gather I/O vector and kernel UIO transfer state.

Key elements:
- Defines public `struct iovec` with base pointer and byte length.
- NetBSD source mode defines `off_t`, `enum uio_rw`, and `enum uio_seg`.
- Kernel or `__UIO_EXPOSE` exposes `struct uio` with iovec array, count, file offset, residual count, read/write direction, and vmspace.
- Defines `UIO_SETUP_SYSSPACE()` and kernel `uio_setup_sysspace()`.
- Defines deprecated `UIO_MAXIOV` and kernel `UIO_SMALLIOV`.
- Userland prototypes expose `readv`, `writev`, and NetBSD `preadv`/`pwritev`.
- Kernel declares `ureadc()`.

Risks and notes:
- `iovec` is public ABI and used by multiple syscalls.
- Kernel `uio` state drives user/kernel and system-space transfer semantics.
