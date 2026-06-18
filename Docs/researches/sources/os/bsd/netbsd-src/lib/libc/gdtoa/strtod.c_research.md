# File Research: sources/os/bsd/netbsd-src/lib/libc/gdtoa/strtod.c

Purpose: Implements locale-aware `strtod`/`strtod_l` for native double.

Core behavior:
- Parses leading whitespace, sign, decimal digits, locale decimal point, and decimal exponent.
- Handles C99 hexadecimal floating constants via `gethex`.
- Handles `inf`, `infinity`, `nan`, and optional hex NaN payloads.
- Uses fast floating-point scaling for easy cases.
- Uses `Bigint` refinement for hard cases to produce the correctly rounded double.
- Handles overflow, underflow, denormals, directed rounding, and optional inexact flag behavior.
- Provides aliases for `strtold` when the platform lacks distinct long double.

Dependencies:
- Includes NetBSD namespace headers, `gdtoaimp.h`, optional `<fenv.h>`, locale headers, and `setlocale_local.h`.
- Uses `s2b`, `d2b`, `pow5mult`, `lshift`, `diff`, `ratio`, `ulp`, `gethex`, `hexnan`, and `ULtod`-style bit packing.
