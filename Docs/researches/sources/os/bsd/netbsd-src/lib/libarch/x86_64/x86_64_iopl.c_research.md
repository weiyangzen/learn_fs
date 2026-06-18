# File Research: sources/os/bsd/netbsd-src/lib/libarch/x86_64/x86_64_iopl.c

Userland wrapper for changing x86_64 I/O privilege level.

Key behavior:
- Exports `x86_64_iopl(int iopl)`.
- Fills `struct x86_64_iopl_args`.
- Calls `sysarch(X86_64_IOPL, &p)`.

Dependencies:
- `machine/sysarch.h`.
