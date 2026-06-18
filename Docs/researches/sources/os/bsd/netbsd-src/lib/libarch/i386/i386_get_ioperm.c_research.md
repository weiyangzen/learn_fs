# File Research: sources/os/bsd/netbsd-src/lib/libarch/i386/i386_get_ioperm.c

Userland wrapper for retrieving the i386 I/O permission bitmap.

Key behavior:
- Exports `i386_get_ioperm(u_long *iomap)`.
- Places the caller pointer in `struct i386_get_ioperm_args`.
- Calls `sysarch(I386_GET_IOPERM, &p)`.

Dependencies:
- `machine/sysarch.h` for the request constant and argument struct.

Notes:
- No null-pointer validation in userland; bad pointers fail through the kernel path.
