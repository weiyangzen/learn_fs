# File Research: sources/os/bsd/netbsd-src/lib/libc/gdtoa/test/ftest.c

Float-format equivalent of `dtest.c`, covering `g_ffmt`, `strtof`, `strtoIf`, `strtopf`, and `strtorf`.

Behavior:
- Accepts rounding mode, digit count, raw one-word hex float, or decimal input.
- For nearest rounding, checks agreement among `strtorf`, `strtopf`, and libc `strtof`.
- Formats floats with `g_ffmt`.
- Reports interval endpoints from `strtoIf` and whether either endpoint equals the rounded float.

Dependencies: `gdtoa.h`, `getround`, float parse/format helpers.
