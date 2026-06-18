# File Research: sources/os/bsd/netbsd-src/lib/libc/gdtoa/strtold_pQ.c

Purpose: Builds `strtold` for quad-precision long double.

Core behavior:
- Defines `GDTOA_LD_FMT` as `Q`.
- Includes `strtold_subr.c`, which expands to `strtold`/`strtold_l` calling `strtopQ`.

Dependencies:
- Depends entirely on `strtold_subr.c` and `strtopQ`.
