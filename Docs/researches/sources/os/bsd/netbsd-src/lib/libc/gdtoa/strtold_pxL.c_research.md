# File Research: sources/os/bsd/netbsd-src/lib/libc/gdtoa/strtold_pxL.c

Purpose: Builds `strtold` for extended long double stored in `xL` format.

Core behavior:
- Defines `GDTOA_LD_FMT` as `xL`.
- Includes `strtold_subr.c`, which expands to `strtold`/`strtold_l` calling `strtopxL`.

Dependencies:
- Depends entirely on `strtold_subr.c` and `strtopxL`.
