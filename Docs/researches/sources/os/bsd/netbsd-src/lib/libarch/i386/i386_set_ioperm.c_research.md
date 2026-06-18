# File Research: sources/os/bsd/netbsd-src/lib/libarch/i386/i386_set_ioperm.c

Userland wrapper for setting the i386 I/O permission bitmap.

Key behavior:
- Exports `i386_set_ioperm(u_long *iomap)`.
- Stores the bitmap pointer in `struct i386_set_ioperm_args`.
- Calls `sysarch(I386_SET_IOPERM, &p)`.

Dependencies:
- `machine/sysarch.h`.

Notes:
- This is a direct ABI shim; validation is deferred to the kernel.
