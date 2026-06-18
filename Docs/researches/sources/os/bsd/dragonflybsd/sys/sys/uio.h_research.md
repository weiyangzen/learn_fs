# File Research: sources/os/bsd/dragonflybsd/sys/sys/uio.h

## Summary
Scatter/gather I/O public declarations and kernel uio helper API.

## Main Responsibilities
- Includes `struct iovec` definitions.
- Defines `off_t` and `ssize_t` as needed under visibility guards.
- For kernel structures, includes `struct uio` and declares `UIO_MAXIOV` and `UIO_SMALLIOV`.
- Declares kernel copy/move helpers for uio, buffers, physical pages, and iovec copyin/free.
- Declares userland `readv`, `writev`, `preadv`, and `pwritev`.

## Important Behavior
Kernel code may allocate iovec arrays only when the caller exceeds the small stack-backed threshold. `iovec_free()` frees only when the allocated vector differs from the supplied stack vector.

## Risks
`UIO_MAXIOV` is a hard ABI/resource limit. Incorrect residual/count handling in users of these APIs can corrupt I/O accounting or copy beyond intended ranges.
