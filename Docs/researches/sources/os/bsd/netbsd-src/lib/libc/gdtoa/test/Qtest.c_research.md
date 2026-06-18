# File Research: sources/os/bsd/netbsd-src/lib/libc/gdtoa/test/Qtest.c

Standalone gdtoa test program for quad-format conversion helpers: `g_Qfmt`, `strtoIQ`, `strtopQ`, and `strtorQ`.

It reads stdin commands for rounding mode (`r`), output digit count (`n`), decimal numbers, or raw 4-word hexadecimal long-double/quad representations. It uses endian-specific `_0.._3` word index macros and compares nearest-rounding `strtorQ` results against `strtopQ`.

Important behavior:
- Maintains current directed rounding mode through `getround`.
- Prints parsed bit patterns and `g_Qfmt` formatted output.
- If the host `long double` looks like 16-byte quad, also prints `%.35Lg`.
- For decimal inputs, tests interval conversion with `strtoIQ`, reporting whether interval endpoints match the rounded result.

Dependencies: `gdtoa.h`, `getround.c`, quad gdtoa conversion/formatting objects, endian configuration macros.
