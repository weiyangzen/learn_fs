# File Research: sources/os/bsd/netbsd-src/lib/libc/gdtoa/test/dItest.c

Small stdin-driven test program for double interval conversion. It compares `strtodI` against `strtoId`.

Core flow:
- Reads one number per line.
- Calls `strtodI(ibuf, &se, dd)` to get two bounding doubles.
- Prints each bound through helper `dshow`, which uses `g_dfmt` and raw double words.
- Calls `strtoId` and reports mismatches in return code, consumed input, or endpoint values.

Dependencies: `gdtoaimp.h`, `g_dfmt`, `strtodI`, `strtoId`.
