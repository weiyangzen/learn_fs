# File Research: sources/os/bsd/netbsd-src/lib/libarch/x86_64/x86_64_mtrr.c

Userland wrappers for x86_64 MTRR get/set operations.

Key behavior:
- `x86_64_get_mtrr(struct mtrr *mtrrp, int *n)` calls `sysarch(X86_64_GET_MTRR, &a)`.
- `x86_64_set_mtrr(struct mtrr *mtrrp, int *n)` calls `sysarch(X86_64_SET_MTRR, &a)`.

Dependencies:
- `machine/sysarch.h` for MTRR structs and request constants.
