# File Research: sources/os/bsd/netbsd-src/lib/libc/gdtoa/qnan.c

Purpose: Build-time helper that generates quiet-NaN bit-pattern definitions.

Core behavior:
- Detects IEEE endian mode from `arith.h`.
- Constructs float and double infinities and subtracts them to produce quiet NaNs.
- Prints `#define` lines for float, double, and long-double NaN words.
- Emits all-ones long-double fallback patterns when `NO_LONG_LONG` is defined.

Dependencies:
- Includes `<stdio.h>` and generated `arith.h`.
- Used by the standalone `makefile` to generate `gd_qnan.h`.
