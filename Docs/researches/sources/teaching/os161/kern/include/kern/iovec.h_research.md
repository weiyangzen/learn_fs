# File Research: sources/teaching/os161/kern/include/kern/iovec.h

Defines `struct iovec` for scatter/gather and kernel I/O plumbing.

Key behavior:
- In kernel builds, `iov_base` is split into a union of `userptr_t iov_ubase` and `void *iov_kbase` to distinguish user-supplied and kernel buffers.
- In userland, exposes POSIX-style `void *iov_base`.
- Always includes `size_t iov_len`.

Relevance:
- SFS block I/O and metadata I/O build `uio` structures backed by `iovec`.
