# File Research: sources/os/bsd/netbsd-src/lib/libc/compat/include/errno.h

Declares old global errno description symbols.

It exposes `sys_nerr` and `sys_errlist[]` inside `__BEGIN_DECLS`.

This preserves ABI for old programs that referenced the historical error-list variables.
