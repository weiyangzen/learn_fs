# File Research: sources/os/bsd/netbsd-src/lib/libc/include/futex_private.h

Private libc futex syscall wrapper header.

Defines inline helpers:
- `__futex`
- `__futex_set_robust_list`
- `__futex_get_robust_list`

They call `_syscall` directly with `SYS___futex` and related syscall numbers, intentionally avoiding `namespace.h`.
