# File Research: sources/os/bsd/netbsd-src/lib/libc/gdtoa/test/ddtest.c

Test driver for double-double gdtoa support: `g_ddfmt`, `strtoIdd`, `strtopdd`, and `strtordd`.

Input model:
- `r` changes directed rounding mode.
- `n` changes digit count for `g_ddfmt`.
- `#` supplies four raw hex words for two doubles.
- A single decimal string tests `strtordd`; two numeric fields can be parsed through native `strtod`.

Important behavior:
- For nearest rounding, checks `strtordd` against `strtopdd`.
- Prints each component double via `g_dfmt`.
- Uses `strtoIdd` to compute interval double-double bounds and compares them against the rounded pair.

Dependencies: `gdtoaimp.h`, `getround`, `g_dfmt`, `g_ddfmt`, double-double parse helpers.
