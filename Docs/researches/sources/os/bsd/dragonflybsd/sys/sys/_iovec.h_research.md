# File Research: sources/os/bsd/dragonflybsd/sys/sys/_iovec.h

Read completely: 48 lines.

This header defines the public `struct iovec` used by vectored I/O APIs.

Key contents:
- Declares `size_t` from machine types if not already declared.
- Defines `struct iovec` with `void *iov_base` and `size_t iov_len`.

Security/reliability notes:
- No runtime behavior. Its layout is ABI-sensitive for `readv`, `writev`, `uio`, and related kernel/user interfaces.
