# File Research: sources/os/bsd/netbsd-src/lib/libarch/i386/i386_iopl.c

Userland wrapper for changing i386 I/O privilege level.

Key behavior:
- Exports `i386_iopl(int iopl)`.
- Stores the requested level in `struct i386_iopl_args`.
- Calls `sysarch(I386_IOPL, &p)`.

Dependencies:
- `machine/sysarch.h`.

Notes:
- Privilege checks and accepted values are enforced by the kernel.
