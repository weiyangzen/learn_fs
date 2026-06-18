# File Research: sources/os/bsd/netbsd-src/lib/libc/resolv/h_errno.c

Provides accessors for resolver host error state. `__h_errno()` returns the address of `_nres.res_h_errno`. `__h_errno_set()` writes both the global `h_errno` compatibility symbol and the supplied resolver state’s `res_h_errno`.

This file bridges old global `h_errno` behavior with resolver-state-based error storage.
