# File Research: sources/os/bsd/netbsd-src/lib/libarch/i386/i386_mtrr.c

Userland wrappers for i386 MTRR get/set operations.

Key behavior:
- `i386_get_mtrr(struct mtrr *mtrrp, int *n)` calls `sysarch(I386_GET_MTRR, &a)`.
- `i386_set_mtrr(struct mtrr *mtrrp, int *n)` calls `sysarch(I386_SET_MTRR, &a)`.
- Both pass the MTRR array pointer and count pointer through the architecture argument structure.

Dependencies:
- `machine/sysarch.h` for `struct mtrr` and request constants.
