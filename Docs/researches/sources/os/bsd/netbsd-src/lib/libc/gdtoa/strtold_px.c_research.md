# File Research: sources/os/bsd/netbsd-src/lib/libc/gdtoa/strtold_px.c

Purpose: Builds `strtold` for extended long double stored in `x` format.

Core behavior:
- Defines `GDTOA_LD_FMT` as `x`.
- Includes `strtold_subr.c`, which expands to `strtold`/`strtold_l` calling `strtopx`.

Dependencies:
- Depends entirely on `strtold_subr.c` and `strtopx`.
