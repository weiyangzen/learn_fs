# File Research: sources/os/bsd/netbsd-src/lib/libarch/i386/i386_set_ldt.c

Userland wrapper for installing i386 LDT descriptors.

Key behavior:
- Exports `i386_set_ldt(int start, union descriptor *desc, int num)`.
- Fills `struct i386_set_ldt_args`.
- Calls `sysarch(I386_SET_LDT, &p)`.

Dependencies:
- `machine/segments.h`.
- `machine/sysarch.h`.

Notes:
- Descriptor validation and privilege checks are kernel-side.
