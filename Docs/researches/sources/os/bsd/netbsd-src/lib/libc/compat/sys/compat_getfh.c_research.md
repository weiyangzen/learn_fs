# File Research: sources/os/bsd/netbsd-src/lib/libc/compat/sys/compat_getfh.c

Read completely: 69 lines.

This implements old `getfh`. It calls `__getfh30` with a `compat_30_fhandle` buffer and size pointer, then verifies the returned size equals `FHANDLE30_SIZE`; otherwise it returns `EINVAL`.

Security/reliability notes: explicit size verification prevents accepting a mismatched file-handle layout.
