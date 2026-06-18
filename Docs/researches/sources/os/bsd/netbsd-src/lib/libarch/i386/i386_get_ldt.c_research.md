# File Research: sources/os/bsd/netbsd-src/lib/libarch/i386/i386_get_ldt.c

Userland wrapper for reading i386 LDT descriptors.

Key behavior:
- Exports `i386_get_ldt(int start, union descriptor *desc, int num)`.
- Fills `struct i386_get_ldt_args` with start index, output descriptor pointer, and count.
- Calls `sysarch(I386_GET_LDT, &p)`.

Dependencies:
- `machine/segments.h` for `union descriptor`.
- `machine/sysarch.h` for the `sysarch` ABI.
